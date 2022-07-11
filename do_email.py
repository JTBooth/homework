from postmarker.core import PostmarkClient

postmark = PostmarkClient(server_token="6fa7fc06-4742-489c-bad4-08c32ede9497")
def send_quiz_link_email(from_addr, to_addr, subject, url):
  if to_addr[-11:] == "jtbooth.com":
    response = postmark.emails.send(
      From=from_addr,
      To=to_addr,
      Subject=subject,
      HtmlBody=f"""
        <html>
          <body>
            <strong>Hello</strong> from Iroha Forms.
            This is the link to your quiz:
            {url}
          </body>
        </html>"""
    )
    print("response:", response)