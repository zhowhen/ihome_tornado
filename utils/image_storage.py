#  coding:utf-8


from qiniu import Auth, put_data
import qiniu.config
#需要填写你的 Access Key 和 Secret Key
access_key = ''
secret_key = ''


def storage(image_data):

    if not image_data:
        return None
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = 'i-home-1'
    # 上传后保存的文件名
    # key = 'my-python-logo.png'
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)
    # 要上传文件的本地路径
    # localfile = './sync/bbb.jpg'
    ret, info = put_data(token, None, image_data)
    # print(info)
    # assert ret['key'] == key
    # assert ret['hash'] == etag(image_data)
    return ret['key']

if __name__ == '__main__':
    file_name = raw_input("请输入文件名:")
    with open(file_name, 'rb') as f:
        file_data = f.read()
        key = storage(file_data)
        print key
