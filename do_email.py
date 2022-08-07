from postmarker.core import PostmarkClient
from email.utils import parseaddr

postmark = PostmarkClient(server_token="6fa7fc06-4742-489c-bad4-08c32ede9497")
def send_quiz_link_email(from_addr, to_addr, subject, url):
  _, to_addr_parsed = parseaddr(to_addr)

  if to_addr_parsed:
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
        </html>""",
      MessageStream="outbound"
    )
    print("response:", response)

def send_feedback_link_email(from_addr, to_addr, subject, url):
  _, to_addr_parsed = parseaddr(to_addr)

  if to_addr_parsed:
    response = postmark.emails.send(
      From=from_addr,
      To=to_addr,
      Subject=subject,
      HtmlBody=f"""
        <html>
          <body>
            <strong>Hello</strong> from Iroha Forms.
            This link will contain your graded quiz once the teacher grades it:
            {url}
          </body>
        </html>""",
      MessageStream="outbound"
    )
    print("response:", response)
