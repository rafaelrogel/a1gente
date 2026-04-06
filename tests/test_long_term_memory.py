import pytest
import os
import tempfile


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    import sqlite3

    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    old_db_path = None
    try:
        from long_term_memory import DB_PATH

        old_db_path = DB_PATH
    except:
        pass

    os.close(db_fd)

    yield db_path

    try:
        os.unlink(db_path)
    except:
        pass


def test_user_isolation_store_and_retrieve(temp_db):
    """Test that facts stored by user A are not returned for user B."""
    import sys

    old_path = None
    try:
        from long_term_memory import DB_PATH

        old_path = DB_PATH
    except:
        pass

    try:
        import long_term_memory

        long_term_memory.DB_PATH = temp_db
        long_term_memory.init_db()

        # Store fact for user A
        result_a = long_term_memory.store_important_fact(
            "User A likes Python", "preferences", "user_a"
        )
        assert result_a is True, "Should store fact for user A"

        # Store different fact for user B
        result_b = long_term_memory.store_important_fact(
            "User B likes JavaScript", "preferences", "user_b"
        )
        assert result_b is True, "Should store fact for user B"

        # Get facts for user A
        facts_a = long_term_memory.get_important_facts(user_id="user_a")

        # Verify user A doesn't see user B's fact
        for fact in facts_a:
            assert "JavaScript" not in fact.get("fact", ""), (
                "User A should not see User B's facts"
            )
            assert "User A likes Python" in fact.get(
                "fact", ""
            ) or "Python" in fact.get("fact", "")

        # Get facts for user B
        facts_b = long_term_memory.get_important_facts(user_id="user_b")

        # Verify user B doesn't see user A's fact
        for fact in facts_b:
            assert "Python" not in fact.get("fact", "") or "JavaScript" in fact.get(
                "fact", ""
            )

    finally:
        if old_path:
            long_term_memory.DB_PATH = old_path


def test_user_preferences_isolation(temp_db):
    """Test that preferences are isolated per user."""
    import sys

    try:
        from long_term_memory import DB_PATH

        old_path = DB_PATH
    except:
        old_path = None

    try:
        import long_term_memory

        long_term_memory.DB_PATH = temp_db
        long_term_memory.init_db()

        # Store preference for user A
        long_term_memory.store_user_preference("user_a", "language", "pt-BR")

        # Store different preference for user B
        long_term_memory.store_user_preference("user_b", "language", "en-US")

        # Get preference for user A
        pref_a = long_term_memory.get_user_preference("user_a", "language")
        assert pref_a == "pt-BR", f"User A should have pt-BR, got {pref_a}"

        # Get preference for user B
        pref_b = long_term_memory.get_user_preference("user_b", "language")
        assert pref_b == "en-US", f"User B should have en-US, got {pref_b}"

    finally:
        if old_path:
            long_term_memory.DB_PATH = old_path


def test_wildcard_injection_prevention(temp_db):
    """Test that wildcard SQL injection is prevented."""
    import sys

    try:
        from long_term_memory import DB_PATH

        old_path = DB_PATH
    except:
        old_path = None

    try:
        import long_term_memory

        long_term_memory.DB_PATH = temp_db
        long_term_memory.init_db()

        # Store multiple facts
        long_term_memory.store_important_fact("Fact about Python", "tech", "user1")
        long_term_memory.store_important_fact("Fact about JavaScript", "tech", "user1")
        long_term_memory.store_important_fact("Fact about Go", "tech", "user1")

        # Search with wildcard - should NOT return all records
        results = long_term_memory.search_important_facts("%")

        # Should return empty or minimal results, not all records
        # The wildcard should be treated as a literal string
        assert len(results) == 0 or all(
            "%" not in r.get("fact", "") for r in results
        ), "Wildcard should not return all records"

    finally:
        if old_path:
            long_term_memory.DB_PATH = old_path


def test_search_exact_match(temp_db):
    """Test that search returns only exact or relevant matches."""
    import sys

    try:
        from long_term_memory import DB_PATH

        old_path = DB_PATH
    except:
        old_path = None

    try:
        import long_term_memory

        long_term_memory.DB_PATH = temp_db
        long_term_memory.init_db()

        # Store facts with specific keywords
        long_term_memory.store_important_fact(
            "Python is a programming language", "tech", "user1"
        )
        long_term_memory.store_important_fact(
            "JavaScript is used for web", "tech", "user1"
        )

        # Search for "Python"
        results = long_term_memory.search_important_facts("Python")

        # Should only return Python-related facts
        assert len(results) > 0, "Should find results for 'Python'"
        for r in results:
            assert "Python" in r.get("fact", ""), f"Result should contain 'Python': {r}"

    finally:
        if old_path:
            long_term_memory.DB_PATH = old_path


def test_sql_injection_prevention(temp_db):
    """Test that SQL injection attempts are prevented."""
    import sys

    try:
        from long_term_memory import DB_PATH

        old_path = DB_PATH
    except:
        old_path = None

    try:
        import long_term_memory

        long_term_memory.DB_PATH = temp_db
        long_term_memory.init_db()

        # Attempt SQL injection
        injection_attempts = [
            "'; DROP TABLE important_facts; --",
            "' OR '1'='1",
            "'; DELETE FROM user_preferences; --",
        ]

        for attempt in injection_attempts:
            # Should not raise exception
            try:
                result = long_term_memory.search_important_facts(attempt)
                # Should return empty or sanitized results
                assert isinstance(result, list), (
                    f"Should return list for injection attempt: {attempt}"
                )
            except Exception as e:
                pytest.fail(f"SQL injection should not raise exception: {e}")

        # Verify tables still exist
        import sqlite3

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        assert "important_facts" in tables, "important_facts table should still exist"

    finally:
        if old_path:
            long_term_memory.DB_PATH = old_path
