import imaplib
import email
from email.header import decode_header
import re  # 新增：用于文件名安全处理
from datetime import datetime
import json
def read_latest_sent_email_attachments(target_subject,lines_set,attachment_lines):
    try:
        # 连接邮箱
        mail = imaplib.IMAP4_SSL('imap.qq.com', 993)
        mail.login("827886863@qq.com", "ehsclmvozlfmbdeg")

        # 选择发件箱
        mail.select('"Sent Messages"')  # 英文账户
        # mail.select('"已发送"')        # 中文账户

        # 按主题过滤邮件
        search_criteria = f'SUBJECT "{target_subject}"'
        status, messages = mail.search(None, search_criteria)
        mail_ids = messages[0].split()

        if not mail_ids:
            print(f"未找到主题包含【{target_subject}】的邮件")
            return

        # 获取最新邮件
        latest_id = mail_ids[-1]
        status, msg_data = mail.fetch(latest_id, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])

        # 解码主题
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")
        print("主题:", subject)

        # 提取正文内容
        def get_body(msg):
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        return part.get_payload(decode=True).decode('utf-8', errors='replace')
            else:
                return msg.get_payload(decode=True).decode('utf-8', errors='replace')
            return ""

        body = get_body(msg)

        # 将正文每行内容存入集合并输出

        for line in body.splitlines():
            cleaned_line = line.strip()  # 去除首尾空白
            if cleaned_line:  # 忽略空行
                lines_set.append(cleaned_line)

        # ====== 新增：提取附件内容 ======


        # 遍历邮件所有部分
        for part in msg.walk():
            # 检查是否为附件 [3,7](@ref)
            if part.get_content_disposition() == 'attachment':
                filename = part.get_filename()

                # 解码文件名（处理编码问题）
                if filename:
                    filename, encoding = decode_header(filename)[0]
                    if isinstance(filename, bytes):
                        filename = filename.decode(encoding or 'utf-8', errors='replace')

                    # 只处理txt文件 [4](@ref)
                    if filename.lower().endswith('注册码.txt'):
                        print(f"找到TXT附件: {filename}")

                        # 安全处理文件名（移除非法字符）
                        safe_filename = re.sub(r'[\\/*?:"<>|]', "", filename)

                        # 获取附件内容并解码
                        attachment_content = part.get_payload(decode=True)
                        try:
                            # 尝试UTF-8解码
                            text_content = attachment_content.decode('utf-8')
                        except UnicodeDecodeError:
                            # 尝试GBK解码（中文环境备用）
                            text_content = attachment_content.decode('gbk', errors='replace')

                        # 按行处理内容 [7](@ref)
                        for line in text_content.splitlines():
                            cleaned_line = line.strip()
                            if cleaned_line:  # 忽略空行
                                attachment_lines.append(cleaned_line)



    except imaplib.IMAP4.error as e:
        print("IMAP错误:", e)
        return []
    except Exception as e:
        print(f"处理错误: {str(e)}")
        return []
    finally:
        try:
            mail.logout()
        except:
            pass



def check_specific_id_expiry(json_data, target_id):
    """检查指定ID是否过期"""
    current_time = datetime.now()
    result = "注册码输入不正确"
    # 分割多行JSON数据
    for i, line in enumerate(json_data, 1):
        try:
            # 解析JSON对象
            entry = json.loads(line)

            # 仅处理目标ID
            if entry["id"] == target_id:
                card_end_time = datetime.strptime(entry["cardEndTime"], "%Y-%m-%d %H:%M:%S")

                # 检查是否过期
                if card_end_time < current_time:
                    print(f"ID {target_id} 已过期 (截止时间: {entry['cardEndTime']})")
                    return "注册码已过期，截止时间为："+entry['cardEndTime']
                else:
                    print(f"ID {target_id} 未过期 (截止时间: {entry['cardEndTime']})")
                    return "OK"

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"解析错误: {e} - 行内容: {line}")

    print(f"未找到ID {target_id}")
    return result


def getCheckResult(loginId):
    resultList = []
    lines_set = list()
    attachment_lines = []  # 存储所有附件内容行的列表
    attachment_content_list = read_latest_sent_email_attachments("tpwUpdate", lines_set, attachment_lines)

    getChek = check_specific_id_expiry(attachment_lines, loginId)
    resultList.append(getChek)
    resultList.append(lines_set)
    return resultList
    # print(f'是否登录过期：{getChek}')
    #
    # print("\n正文内容集合:")
    # for line in lines_set:
    #     print(line)

    # print("\n附件内容行列表:")
    # for i, line in enumerate(attachment_lines, 1):
    #     print(f"{line}")


resultList = getCheckResult("12313")
# print(f'是否登录过期：{resultList[0]}')
#
print(f"{resultList[1][0]}")
text =""
for i,line in enumerate(resultList[1]):
    if(i > 0 ):
        text =text+line+"\n"

print(text)


