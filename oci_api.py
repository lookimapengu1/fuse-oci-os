import oci
import io

cfg = oci.config.from_file()
obj = oci.object_storage.object_storage_client.ObjectStorageClient(cfg)
bucket_name = 'william-scotsmen-test'
cmpt_id = cfg['compartment']
ns = obj.get_namespace()

#ls command for files
def ls_files(bn):
    bkts = obj.list_objects(ns.data, bn)
    data = []
    for b in bkts.data.objects:
        data.append(b.name)
        #data = data + b.name + " "
    #print data
    return data

#rm command for files
def rm_file(self, bn, to_delete):
    for b in bkts.data.objects:
        if b.name == to_delete:
            print 'deleting file', to_delete, 'now'
            obj.delete_object(ns.data, bn, b.name)

#cp command for files
def cp_file(self, bn, to_upload):
    to_upload = obj.put_object(ns.data, bucket_name, to_create, io.open(to_create))
