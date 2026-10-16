# Scalable Cloud Clip Farm — quick deployment guide

**Do not purchase a VPS or run paid video APIs without the user's consent.**

## Cheap paths
- Start free: one private GitHub Codespace running the base app, on demand. It stops when idle and is unsuitable for autonomous 24/7 clipping. Default includes CPU quota; Codespaces storage is not a long-video archive.
- After approving ~$10/month: one Hetzner CX33 in a European region (4 shared vCPU, 8GB RAM; **October 2026 list price US $9.99/month excluding VAT/IPv4, storage extras**) plus optional object storage. Ensure server has sufficient *scratch disk* for video ingest/rendering; CX33 storage is not unlimited.
- Don't clone a separate VM for each social account. Run one queue with account/brand tags, and 2-3 worker replicas on the same VPS. Two cores don't become six because there are three worker processes.

## Local or cloud VM Linux quickstart (Docker installed)
The ZIP contains the complete original Clip Farm and Creator Studio, plus this deployment layer.
```bash
unzip ai-cloud-lab-scalable-clip-farm.zip
cd ai-cloud-lab-scalable-clip-farm
mkdir -p farm-data/{inputs,outputs,state}
printf 'FARM_DIR=./farm-data\nHOST_UID=%s\nHOST_GID=%s\n' "$(id -u)" "$(id -g)" > .env
docker compose -f compose.clipfarm.yml build
docker compose -f compose.clipfarm.yml up -d --scale worker=2
docker compose -f compose.clipfarm.yml ps
```
If the downloaded ZIP has a different top-level directory name, `cd` into the one containing compose.clipfarm.yml.

## Add an authorized long video
Transfer authorized footage into `farm-data/inputs/long.mp4` (SFTP, rsync, or local upload; HTTPS direct-download commands from the original `docs/CLIP_FARM.md`). Keep enough local temporary disk free.
```bash
docker compose -f compose.clipfarm.yml run --rm worker \
   python -m farmworker --root /farm enqueue \
   --source long.mp4 --brand tech-channel --clips 12 \
   --profile tiktok --rights-confirmed
docker compose -f compose.clipfarm.yml logs -f --tail=40 worker
docker compose -f compose.clipfarm.yml run --rm worker python -m farmworker --root /farm list
```
Approved rights are required, including for video downloads. Input paths must live inside the private farm-data/inputs directory. `enqueue` creates clip-preview jobs only; **it does not post online**.

Find `farm-data/outputs/tech-channel/<job-id>/previews/` and review the suggested clips. To render approved cuts, edit clip-plan.json, remove unwanted clips, mark selected ones `"approved": true`, and run:
```bash
docker compose -f compose.clipfarm.yml run --rm worker \
   python -m clipfarm.cli render \
   --plan /farm/outputs/tech-channel/JOB_ID/clip-plan.json \
   --outdir /farm/outputs/tech-channel/JOB_ID/finals \
   --profile tiktok --threads 2 --workers 1
```
`JOB_ID` is printed by the enqueue command. Create account upload drafts using the original `clipfarm.cli accounts` command. Publishing APIs are not configured, and nothing bypasses platform limits.

## Scale within the same VM (same shared queue)
```bash
docker compose -f compose.clipfarm.yml up -d --scale worker=3
docker compose -f compose.clipfarm.yml ps
docker compose -f compose.clipfarm.yml stop
```
Scale back to one worker if the host starts swapping or processing becomes slower. Each worker has 1 CPU and 2 GB RAM limits by default; actual availability depends on the VPS resources.

## Run completely separate client farms on one machine
For strong client or brand data separation, run separate Compose *projects*, each with separate local farm directories (and separate SQLite databases). Do not put media for unrelated clients in the same bucket without scoped access controls.
```bash
mkdir -p /srv/client-a/farm-data /srv/client-b/farm-data
# Make directories writable by the host user before starting containers.
FARM_DIR=/srv/client-a/farm-data docker compose -p client-a -f compose.clipfarm.yml up -d --scale worker=2
FARM_DIR=/srv/client-b/farm-data docker compose -p client-b -f compose.clipfarm.yml up -d --scale worker=1
```
Two separate farms on ONE server still share its CPU/RAM/disk. To span multiple servers, replace this SQLite/local-drive queue with an appropriate shared task broker (Redis Streams, SQS, or Postgres), plus object storage; never share a SQLite file across network disks.

## Save money and protect the deployment
- For simple keyframe cut jobs, the original CLI offers `--fast-copy`; no transcoding, but no reframe/captions and cuts may be imprecise.
- Store source files temporarily on SSD; move outputs to R2 and delete scratch only **after verifying upload and backup**.
- Set a storage quota and monitoring alerts. A source 40 GB + previews + outputs can exceed the disk of a small VPS.
- Don't expose the noVNC/RDP desktop publicly: keep Codespaces forwarded port private, or use a private tunnel/VPN with strong authentication.
- Use the social accounts' official APIs with permissions, respect copyrights, creator consent, platform limits, and policies. No automated mass registrations or evading bans.
- No provider accounts or charges are created by this ZIP. `docker compose up` starts local/approved-host containers only.

## Validation
```bash
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s deploy/tests -v
```
