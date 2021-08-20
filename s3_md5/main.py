import boto3
import os 
import hashlib


AWS_PROFILE = ''
SESSION = boto3.session.Session(profile_name=f'{AWS_PROFILE}')
BUCKET = ''
BUCKET_PATH = ''


def calculate_file_md5(filename):
    m = hashlib.md5()
    with open(filename, 'rb') as f:
        for data in iter(lambda: f.read(1024 * 1024), b''):
            m.update(data)

    return m.hexdigest()

def download_files(bucket, folder, filter):
    return_data = ''
    s3 = SESSION.resource('s3')
    b = s3.Bucket(bucket)
    for obj in b.objects.filter(Prefix=folder):
        print(obj.key)
        path, filename = os.path.split(obj.key)
        if filter in filename:
            b.download_file(obj.key, filename.strip(folder))
            return_data += (f'{filename} - {calculate_file_md5(filename)}\n')
            os.remove(filename)

    with open('md5_list.txt', 'w') as f:
        f.write(return_data)



if __name__ == '__main__':
    download_files(
        bucket=f'{BUCKET}',
        folder=f'{BUCKET_PATH}',
        filter='2020-02-28'
    )
