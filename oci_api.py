import oci
import io

cfg = oci.config.from_file()
obj = oci.object_storage.object_storage_client.ObjectStorageClient(cfg)
bucket_name = 'william-scotsmen-test'
cmpt_id = cfg['compartment']
ns = obj.get_namespace()

#print cfg["compartment"]

#ls command for files
bkts = obj.list_objects(ns.data, bucket_name)
for b in bkts.data.objects:
    print b.name

#rm command for files
to_delete = raw_input('File to delete: ')
for b in bkts.data.objects:
    if b.name == to_delete:
        print 'deleting file', to_delete, 'now'
        obj.delete_object(ns.data, bucket_name, b.name)

#touch command for files
to_create = raw_input('File to upload: ')
to_upload = obj.put_object(ns.data, bucket_name, to_create, io.open(to_create))
