import json
import logging
import os
from urllib.request import urlopen

BASE_URL = "https://www.nic.cz/public_media/blocked_outzone_domains/admin_blocked_outzone_domains_reason.json"
HTTP_TIMEOUT = 30


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    tfn = "blocked_domains.json"
    changelog = []
    stats = [0, 0, 0]

    existing = []
    if os.path.isfile(tfn):
        with open(tfn, "rt", encoding="utf-8") as f:
            existing = json.load(f)

    with urlopen(BASE_URL, timeout=HTTP_TIMEOUT) as r:
        new_data = json.load(r)
        assert set(new_data.keys()) == {"generated_at", "data"}
        new_data = new_data["data"]

    with open(tfn, "w", encoding="utf-8") as fw:
        json.dump(new_data, fw, indent=2, ensure_ascii=False, sort_keys=True)

    old = {j["fqdn"]: j for j in existing}
    new = {j["fqdn"]: j for j in new_data}

    for added in new.keys() - old.keys():
        changelog.append(f"Nová doména: {added} ({new[added]['reason']})")
        stats[0] += 1

    for deleted in old.keys() - new.keys():
        changelog.append(f"Odebraná doména: {added}")
        stats[1] += 1

    for sid in old.keys() & new.keys():
        if json.dumps(old[sid]) != json.dumps(new[sid]):
            changelog.append(f"Změněná doména: {sid}")
            stats[2] += 1

if len(changelog) > 0:
    print(
        f"Nové: {stats[0]}, zrušené: {stats[1]}, změněné: {stats[2]}. Celkem: {len(new_data)}"
    )
    print("\n".join(sorted(changelog)))
