set -e

cd ../.devcontainer/config

rm -f \
    .storage/core.device_registry \
    .storage/core.entity_registry \
    .storage/core.config_entries \
    .storage/core.restore_state \
    home-assistant_v2.db \
    home-assistant_v2.db-shm \
    home-assistant_v2.db-wal
    
echo 'Purged registries and recorder DB.'
