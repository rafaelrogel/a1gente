import logging
import tweepy
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

_twitter_client = None
_twitter_client_v1 = None


def get_twitter_client():
    global _twitter_client
    if _twitter_client is not None:
        return _twitter_client

    try:
        from config import (
            TWITTER_API_KEY,
            TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN,
            TWITTER_ACCESS_SECRET,
            TWITTER_BEARER_TOKEN,
        )

        if not all(
            [
                TWITTER_API_KEY,
                TWITTER_API_SECRET,
                TWITTER_ACCESS_TOKEN,
                TWITTER_ACCESS_SECRET,
            ]
        ):
            logger.warning("Twitter credentials not fully configured")
            return None

        _twitter_client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET,
            bearer_token=TWITTER_BEARER_TOKEN,
        )
        return _twitter_client
    except ImportError:
        logger.error("tweepy not installed. Run: pip install tweepy")
        return None
    except Exception as e:
        logger.error(f"Error initializing Twitter client: {e}")
        return None


def get_twitter_client_v1():
    global _twitter_client_v1
    if _twitter_client_v1 is not None:
        return _twitter_client_v1

    try:
        from config import (
            TWITTER_API_KEY,
            TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN,
            TWITTER_ACCESS_SECRET,
        )

        if not all(
            [
                TWITTER_API_KEY,
                TWITTER_API_SECRET,
                TWITTER_ACCESS_TOKEN,
                TWITTER_ACCESS_SECRET,
            ]
        ):
            return None

        auth = tweepy.OAuth1UserHandler(
            TWITTER_API_KEY,
            TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN,
            TWITTER_ACCESS_SECRET,
        )
        _twitter_client_v1 = tweepy.API(auth)
        return _twitter_client_v1
    except Exception as e:
        logger.error(f"Error initializing Twitter v1 client: {e}")
        return None


async def post_tweet(text: str) -> str:
    client = get_twitter_client()
    if not client:
        return "⚠️ Twitter não configurado. Configure as credenciais API."

    if len(text) > 280:
        text = text[:277] + "..."

    try:
        response = client.create_tweet(text=text)
        tweet_id = response.data["id"]
        tweet_url = f"https://twitter.com/user/status/{tweet_id}"
        return f"✅ Tweet postado com sucesso!\n{tweet_url}"
    except tweepy.errors.TweepyException as e:
        logger.error(f"Twitter API error: {e}")
        return f"❌ Erro ao postar tweet: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error posting tweet: {e}")
        return f"❌ Erro inesperado: {str(e)}"


async def get_tweet(tweet_id: str) -> str:
    client = get_twitter_client()
    if not client:
        return "⚠️ Twitter não configurado."

    try:
        response = client.get_tweet(
            tweet_id, tweet_fields=["created_at", "author_id", "public_metrics", "text"]
        )

        if not response.data:
            return "⚠️ Tweet não encontrado."

        tweet = response.data
        metrics = tweet.public_metrics if hasattr(tweet, "public_metrics") else {}

        result = f"""📝 Tweet ID: {tweet_id}
👤 Author ID: {tweet.author_id}
📅 Created: {tweet.created_at}
📊 Likes: {metrics.get("like_count", "N/A")} | Retweets: {metrics.get("retweet_count", "N/A")} | Replies: {metrics.get("reply_count", "N/A")}

💬 Text:
{tweet.text}

🔗 https://twitter.com/user/status/{tweet_id}"""
        return result
    except tweepy.errors.TweepyException as e:
        return f"❌ Erro ao buscar tweet: {str(e)}"
    except Exception as e:
        return f"❌ Erro inesperado: {str(e)}"


async def search_tweets(query: str, max_results: int = 10) -> str:
    client = get_twitter_client()
    if not client:
        return "⚠️ Twitter não configurado."

    max_results = min(max_results, 100)

    try:
        response = client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=["created_at", "author_id", "public_metrics"],
        )

        if not response.data:
            return f"⚠️ Nenhum tweet encontrado para: '{query}'"

        results = []
        for i, tweet in enumerate(response.data, 1):
            metrics = tweet.public_metrics if hasattr(tweet, "public_metrics") else {}
            results.append(f"""{i}. Tweet ID: {tweet.id}
   👤 Author ID: {tweet.author_id}
   📅 {tweet.created_at}
   💬 {tweet.text[:200]}{"..." if len(tweet.text) > 200 else ""}
   ❤️ {metrics.get("like_count", 0)} | 🔄 {metrics.get("retweet_count", 0)} | 💬 {metrics.get("reply_count", 0)}""")

        return f"🔍 Resultados para '{query}':\n\n" + "\n\n".join(results)
    except tweepy.errors.TweepyException as e:
        return f"❌ Erro na busca: {str(e)}"
    except Exception as e:
        return f"❌ Erro inesperado: {str(e)}"


async def get_user_timeline(username: str, count: int = 10) -> str:
    client = get_twitter_client()
    if not client:
        return "⚠️ Twitter não configurado."

    count = min(count, 100)

    try:
        user_response = client.get_user(username=username)
        if not user_response.data:
            return f"⚠️ Usuário '{username}' não encontrado."

        user_id = user_response.data.id

        tweets_response = client.get_users_tweets(
            user_id, max_results=count, tweet_fields=["created_at", "public_metrics"]
        )

        if not tweets_response.data:
            return f"⚠️ Nenhum tweet encontrado para @{username}"

        results = []
        for i, tweet in enumerate(tweets_response.data, 1):
            metrics = tweet.public_metrics if hasattr(tweet, "public_metrics") else {}
            results.append(f"""{i}. Tweet ID: {tweet.id}
   📅 {tweet.created_at}
   💬 {tweet.text[:200]}{"..." if len(tweet.text) > 200 else ""}
   ❤️ {metrics.get("like_count", 0)} | 🔄 {metrics.get("retweet_count", 0)}""")

        return f"📅 Timeline de @{username}:\n\n" + "\n\n".join(results)
    except tweepy.errors.TweepyException as e:
        return f"❌ Erro ao buscar timeline: {str(e)}"
    except Exception as e:
        return f"❌ Erro inesperado: {str(e)}"


async def get_user_info(username: str) -> str:
    client = get_twitter_client()
    if not client:
        return "⚠️ Twitter não configurado."

    try:
        response = client.get_user(
            username=username,
            user_fields=[
                "created_at",
                "description",
                "public_metrics",
                "location",
                "verified",
            ],
        )

        if not response.data:
            return f"⚠️ Usuário '{username}' não encontrado."

        user = response.data
        metrics = user.public_metrics if hasattr(user, "public_metrics") else {}

        verified_badge = "✅" if hasattr(user, "verified") and user.verified else ""

        result = f"""👤 @{username} {verified_badge}
📝 Bio: {getattr(user, "description", "N/A")}
📍 Location: {getattr(user, "location", "N/A")}
📅 Joined: {getattr(user, "created_at", "N/A")}
📊 Followers: {metrics.get("followers_count", "N/A")} | Following: {metrics.get("following_count", "N/A")} | Tweets: {metrics.get("tweet_count", "N/A")}
🔗 https://twitter.com/{username}"""
        return result
    except tweepy.errors.TweepyException as e:
        return f"❌ Erro ao buscar usuário: {str(e)}"
    except Exception as e:
        return f"❌ Erro inesperado: {str(e)}"


async def like_tweet(tweet_id: str) -> str:
    client = get_twitter_client()
    if not client:
        return "⚠️ Twitter não configurado."

    try:
        client.like(tweet_id)
        return f"❤️ Tweet {tweet_id} curtido com sucesso!"
    except tweepy.errors.TweepyException as e:
        return f"❌ Erro ao curtir tweet: {str(e)}"
    except Exception as e:
        return f"❌ Erro inesperado: {str(e)}"


async def retweet(tweet_id: str) -> str:
    client = get_twitter_client()
    if not client:
        return "⚠️ Twitter não configurado."

    try:
        client.retweet(tweet_id)
        return f"🔄 Tweet {tweet_id} retweetado com sucesso!"
    except tweepy.errors.TweepyException as e:
        return f"❌ Erro ao retweetar: {str(e)}"
    except Exception as e:
        return f"❌ Erro inesperado: {str(e)}"


async def reply_to_tweet(tweet_id: str, text: str) -> str:
    client = get_twitter_client()
    if not client:
        return "⚠️ Twitter não configurado."

    if len(text) > 280:
        text = text[:277] + "..."

    try:
        response = client.create_tweet(text=text, in_reply_to_tweet_id=tweet_id)
        reply_id = response.data["id"]
        return f"✅ Resposta postada!\nTweet ID: {reply_id}\n🔗 https://twitter.com/user/status/{reply_id}"
    except tweepy.errors.TweepyException as e:
        return f"❌ Erro ao responder: {str(e)}"
    except Exception as e:
        return f"❌ Erro inesperado: {str(e)}"


async def delete_tweet(tweet_id: str) -> str:
    client = get_twitter_client()
    if not client:
        return "⚠️ Twitter não configurado."

    try:
        client.delete_tweet(tweet_id)
        return f"🗑️ Tweet {tweet_id} deletado com sucesso!"
    except tweepy.errors.TweepyException as e:
        return f"❌ Erro ao deletar tweet: {str(e)}"
    except Exception as e:
        return f"❌ Erro inesperado: {str(e)}"
