from .. import DerivedBase, Property, Base, Region

class Backup(DerivedBase):
    api_endpoint = '/linode/instances/{linode_id}/backups/{id}'
    derived_url_path = 'backups'
    parent_id_name='linode_id'

    properties = {
        'id': Property(identifier=True),
        'created': Property(is_datetime=True),
        'duration': Property(),
        'finished': Property(is_datetime=True),
        'message': Property(),
        'status': Property(volatile=True),
        'type': Property(),
        'linode_id': Property(identifier=True),
        'label': Property(),
        'configs': Property(),
        'disks': Property(),
        'availability': Property(),
        'region': Property(slug_relationship=Region),
    }

    def restore_to(self, linode, **kwargs):
        d = {
            "linode_id": linode.id if issubclass(type(linode), Base) else linode,
        }
        d.update(kwargs)

        result = self._client.post("{}/restore".format(Backup.api_endpoint), model=self,
            data=d)
        return True
