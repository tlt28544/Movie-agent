def render_email(date_str: str, movies_with_cards: list[dict], top20_movies: list[dict]) -> str:
    cards = []
    for item in movies_with_cards:
        movie = item["movie"]
        card = item["analysis"]

        why_now_html = "".join(f"<li>{w}</li>" for w in card.get("why_now", [])[:3])
        watch = "、".join(card.get("who_should_watch", []))
        similar = "、".join(card.get("similar_titles", []))
        starring = "、".join(card.get("starring_cast", [])[:5]) or "暂无"

        cards.append(
            f"""
            <div style='border:1px solid #ddd;border-radius:12px;padding:14px;margin:12px 0;'>
              <h3 style='margin:0 0 8px 0;'>{movie.get('title')} ({movie.get('year') or 'N/A'})</h3>
              <p style='margin:0 0 8px 0;color:#333;'><b>一句话：</b>{card.get('one_liner','')}</p>
              <p style='margin:0 0 8px 0;color:#333;'><b>推荐理由：</b>{card.get('recommendation','')}</p>
              <ul style='margin:6px 0 8px 18px;padding:0;'>{why_now_html}</ul>
              <p style='margin:6px 0;'><b>影片简介：</b>{card.get('movie_profile','')}</p>
              <p style='margin:6px 0;'><b>导演背景：</b>{card.get('director_background','')}</p>
              <p style='margin:6px 0;'><b>明星演员：</b>{starring}</p>
              <p style='margin:6px 0;'><b>适合：</b>{watch}</p>
              <p style='margin:6px 0;'><b>类似影片：</b>{similar}</p>
              <p style='margin:6px 0;'><a href='{movie.get('url')}' target='_blank'>查看影片详情</a></p>
            </div>
            """
        )

    table_rows = "".join(
        f"<tr><td style='border:1px solid #ddd;padding:6px;'>#{m.get('rank')}</td>"
        f"<td style='border:1px solid #ddd;padding:6px;'>{m.get('title')}</td>"
        f"<td style='border:1px solid #ddd;padding:6px;'>{m.get('year') or 'N/A'}</td>"
        f"<td style='border:1px solid #ddd;padding:6px;'>{m.get('vote_average') or 'N/A'}</td></tr>"
        for m in top20_movies[:20]
    )

    return f"""
    <html>
      <body style='font-family:Arial,Helvetica,sans-serif;max-width:760px;margin:0 auto;padding:16px;'>
        <h2 style='margin-bottom:6px;'>🎬 movie-agent 每日推荐（中文）</h2>
        <p style='color:#666;margin-top:0;'>日期：{date_str}</p>
        {''.join(cards)}
        <h3 style='margin-top:20px;'>最新 Top20 榜单</h3>
        <table style='border-collapse:collapse;width:100%;font-size:14px;'>
          <thead>
            <tr>
              <th style='border:1px solid #ddd;padding:6px;'>排名</th>
              <th style='border:1px solid #ddd;padding:6px;'>片名</th>
              <th style='border:1px solid #ddd;padding:6px;'>年份</th>
              <th style='border:1px solid #ddd;padding:6px;'>评分</th>
            </tr>
          </thead>
          <tbody>
            {table_rows}
          </tbody>
        </table>
      </body>
    </html>
    """.strip()
