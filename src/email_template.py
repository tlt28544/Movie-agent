def render_email(date_str: str, movies_with_cards: list[dict], top30_movies: list[dict]) -> str:
    cards = []
    for item in movies_with_cards:
        movie = item["movie"]
        card = item["analysis"]

        why_now_html = "".join(f"<li>{w}</li>" for w in card.get("why_now", [])[:3])
        watch = ", ".join(card.get("who_should_watch", []))
        similar = ", ".join(card.get("similar_titles", []))
        starring = ", ".join(card.get("starring_cast", [])[:5]) or "N/A"

        cards.append(
            f"""
            <div style='border:1px solid #ddd;border-radius:12px;padding:14px;margin:12px 0;'>
              <h3 style='margin:0 0 8px 0;'>{movie.get('title')} ({movie.get('year') or 'N/A'})</h3>
              <p style='margin:0 0 8px 0;color:#333;'><b>One-liner:</b> {card.get('one_liner','')}</p>
              <p style='margin:0 0 8px 0;color:#333;'><b>Why we recommend it:</b> {card.get('recommendation','')}</p>
              <ul style='margin:6px 0 8px 18px;padding:0;'>{why_now_html}</ul>
              <p style='margin:6px 0;'><b>Movie profile:</b> {card.get('movie_profile','')}</p>
              <p style='margin:6px 0;'><b>Director background:</b> {card.get('director_background','')}</p>
              <p style='margin:6px 0;'><b>Starring cast:</b> {starring}</p>
              <p style='margin:6px 0;'><b>Best for:</b> {watch}</p>
              <p style='margin:6px 0;'><b>Similar titles:</b> {similar}</p>
              <p style='margin:6px 0;'><a href='{movie.get('url')}' target='_blank'>View movie details</a></p>
            </div>
            """
        )

    table_rows = "".join(
        f"<tr><td style='border:1px solid #ddd;padding:6px;'>#{m.get('rank')}</td>"
        f"<td style='border:1px solid #ddd;padding:6px;'>{m.get('title')}</td>"
        f"<td style='border:1px solid #ddd;padding:6px;'>{m.get('year') or 'N/A'}</td>"
        f"<td style='border:1px solid #ddd;padding:6px;'>{m.get('vote_average') or 'N/A'}</td></tr>"
        for m in top30_movies[:30]
    )

    return f"""
    <html>
      <body style='font-family:Arial,Helvetica,sans-serif;max-width:760px;margin:0 auto;padding:16px;'>
        <h2 style='margin-bottom:6px;'>🎬 movie-agent Daily Recommendations</h2>
        <p style='color:#666;margin-top:0;'>Date: {date_str}</p>
        {''.join(cards)}
        <h3 style='margin-top:20px;'>Latest Top 30 Trending List</h3>
        <table style='border-collapse:collapse;width:100%;font-size:14px;'>
          <thead>
            <tr>
              <th style='border:1px solid #ddd;padding:6px;'>Rank</th>
              <th style='border:1px solid #ddd;padding:6px;'>Title</th>
              <th style='border:1px solid #ddd;padding:6px;'>Year</th>
              <th style='border:1px solid #ddd;padding:6px;'>Rating</th>
            </tr>
          </thead>
          <tbody>
            {table_rows}
          </tbody>
        </table>
      </body>
    </html>
    """.strip()
