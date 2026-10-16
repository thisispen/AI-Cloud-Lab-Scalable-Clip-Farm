#!/usr/bin/env python3
"""Private R2 object uploads; requires user-provided scoped bucket credentials."""
import argparse, os, sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1]/'.env')

def client_and_bucket():
    import boto3
    keys=('R2_ACCOUNT_ID','R2_ACCESS_KEY_ID','R2_SECRET_ACCESS_KEY','R2_BUCKET')
    missing=[k for k in keys if not os.environ.get(k)]
    if missing: raise RuntimeError('Missing configuration: '+', '.join(missing))
    endpoint=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com"
    c=boto3.client('s3',endpoint_url=endpoint,aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],region_name='auto')
    return c,os.environ['R2_BUCKET']

def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='action',required=True)
    sub.add_parser('check')
    u=sub.add_parser('upload');u.add_argument('filename');u.add_argument('--key',default=None)
    args=p.parse_args()
    try:
        c,b=client_and_bucket()
        if args.action=='check':
            c.head_bucket(Bucket=b);print(f'R2 bucket reachable: {b}')
        else:
            f=Path(args.filename)
            if not f.is_file(): p.error('File not found: '+str(f))
            key=args.key or f.name
            c.upload_file(str(f),b,key)
            print(f'Uploaded private R2 object: {b}/{key}')
    except Exception as e:
        print(f'R2 error: {e}',file=sys.stderr);sys.exit(1)
if __name__=='__main__':main()
