class Image(object):

    def __init__(self, image_info, name=None, image_id=None, creation_date=None, snapshots=None, ttl_days=14):
        self.image_info = image_info
        self.name = name
        self.image_id = image_id
        self.creation_date = creation_date
        self.snapshots = snapshots
        self.ttl_days = ttl_days # time to live, in days
        self.init_image_info()

    def init_image_info(self):
        self.set_name()
        self.set_image_id()
        self.set_creation_date()
        self.set_snapshots()

    def set_name(self):
        if not self.name:
            self.name = self.image_info['Name']

    def set_image_id(self):
        if not self.image_id:
            self.image_id = self.image_info['ImageId']

    def set_creation_date(self):
        if not self.creation_date:
            self.creation_date = self.image_info['CreationDate']

    def set_snapshots(self):
        if not self.snapshots:
            try:
                volumes = self.image_info['BlockDeviceMappings']
                self.snapshots = [volume['Ebs']['SnapshotId'] for volume in volumes if 'Ebs' in volume and 'SnapshotId' in volume['Ebs']]
            except:
                self.snapshots = []


