from postmarker.core import PostmarkClient
from email.utils import parseaddr
from flask import current_app

# Server token deactivated due to accidentally publicizing it on github
# TODO store it in the environment
postmark = PostmarkClient(server_token="6fa7fc06-4742-489c-bad4-08c32ede9497")
def send_quiz_link_email(from_addr, to_addr, subject, teacher_url, student_url, quiz_name):
  _, to_addr_parsed = parseaddr(to_addr)

  if current_app.config['REALLY_SEND_EMAILS']:
    if to_addr_parsed:
      response = postmark.emails.send(
        From=from_addr,
        To=to_addr,
        Subject=subject,
        HtmlBody=f"""
          <html>
            <body>
              いろはフォームで問題「<b>{quiz_name}</b>」が作成されました。<br>
              生徒に共有するリンクはこちらです：{student_url}<br>
              採点はこちらのリンクから：{teacher_url}
            </body>
          </html>""",
        MessageStream="outbound"
      )
      print("response:", response)
  else:
    print('sent quiz link email')

def send_feedback_link_email(from_addr, to_addr, subject, url, teacher_name, quiz_name):
  _, to_addr_parsed = parseaddr(to_addr)

  if current_app.config['REALLY_SEND_EMAILS'] or True:
    if to_addr_parsed:
      response = postmark.emails.send(
        From=from_addr,
        To=to_addr,
        Subject=subject,
        HtmlBody=f"""
          <html>
            <body>
              いろはフォームで<b>{teacher_name}</b>先生の試験「<b>{quiz_name}</b>」が提出されました。<br>
              先生の採点後、こちらのリンクから採点結果を見ることができます。<br>
              {url}
            </body>
          </html>""",
        MessageStream="outbound"
      )
      print("response:", response)
  else:
    print('sent feedback link email')
