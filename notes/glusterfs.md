#### XFS filesystem
    yum install xfsdump xfsprogs.x86_64 xfsprogs-devel.x86_64 xfsprogs-qa-devel.x86_64
    modprobe xfs

#### Format and mount the bricks
    mkfs.xfs -i size=512 /dev/sdb1
    mkdir -p /data/brick1
    echo "/dev/sdb1 /data/brick1 xfs defaults 1 2" >> /etc/fstab
    mount -a && mount

#### Installing GlusterFS
    wget -P /etc/yum.repos.d http://download.gluster.org/pub/gluster/glusterfs/LATEST/RHEL/glusterfs-epel.repo
    yum install glusterfs-server glusterfs-geo-replication
    service glusterd start
    service glusterd status

#### Configure the trusted pool(from node1)
    gluster peer probe node2

#### Set up a GlusterFS volume(on both node1 and node2)
    mkdir /data/brick1/gv0

From any single server

    gluster volume create gv0 replica 2 node1:/data/brick1/gv0 node2:/data/brick1/gv0
    gluster volume start gv0

Confirm that the volume shows "Started":

    gluster volume info
        volume start: gv0: success

#### Testing the GlusterFS volume
    mkdir -p /mnt/glusterfs
    mount -t glusterfs node1:/gv0 /mnt/glusterfs

#### Starting glusterd Automatically
    chkconfig glusterd on
