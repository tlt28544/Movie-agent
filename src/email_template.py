def render_email(date_str: str, movies_with_cards: list[dict]) -> str:
    cards = []
    for item in movies_with_cards:
        movie = item["movie"]
        card = item["analysis"]

        why_now_html = "".join(f"<li>{w}</li>" for w in card.get("why_now", [])[:3])
        watch = "、".join(card.get("who_should_watch", []))
        avoid = "、".join(card.get("who_should_avoid", []))
        similar = ", ".join(card.get("similar_titles", []))

        cards.append(
            f"""
            <div style='border:1px solid #ddd;border-radius:12px;padding:14px;margin:12px 0;'>
              <h3 style='margin:0 0 8px 0;'>{movie.get('title')} ({movie.get('year') or 'N/A'})</h3>
              <p style='margin:0 0 8px 0;color:#333;'>{card.get('one_liner','')}</p>
              <ul style='margin:6px 0 8px 18px;padding:0;'>{why_now_html}</ul>
              <p style='margin:6px 0;'><b>适合：</b>{watch}</p>
              <p style='margin:6px 0;'><b>避雷：</b>{avoid}</p>
              <p style='margin:6px 0;'><b>类似影片：</b>{similar}</p>
              <p style='margin:6px 0;'><a href='{movie.get('url')}' target='_blank'>查看影片详情</a></p>
            </div>
            """
        )

    return f"""
    <html>
      <body style='font-family:Arial,Helvetica,sans-serif;max-width:680px;margin:0 auto;padding:16px;'>
        <h2 style='margin-bottom:6px;'>🎬 movie-agent 每日推荐</h2>
        <p style='color:#666;margin-top:0;'>日期：{date_str}</p>
        {''.join(cards)}
      </body>
    </html>
    """.strip()
