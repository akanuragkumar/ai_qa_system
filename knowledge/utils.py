from django.db import connection


def search_similar_documents(query_embedding, top_k=3):
    # Convert embedding list into PostgreSQL vector format (square brackets)
    embedding_array = f"[{','.join(map(str, query_embedding))}]"

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT id, title, content, embedding <=> %s::vector AS distance
            FROM document
            ORDER BY distance ASC
            LIMIT %s;
            """,
            [embedding_array, top_k]  # Pass as a query parameter to avoid SQL injection
        )
        results = cursor.fetchall()

    return [
        {"id": row[0], "title": row[1], "content": row[2], "distance": row[3]}
        for row in results
    ]
