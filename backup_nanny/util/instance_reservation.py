class InstanceReservation(object):

    def __init__(self, reservation_info, instance_id=None, name=None):
        self.reservation_info = reservation_info 
        self.instance_id = instance_id
        self.name = name
        self.init_instance_info()

    def init_instance_info(self):
        self.set_name()
        self.set_instance_id()

    def set_instance_id(self):
        if not self.instance_id:
            self.instance_id = self.get_instance_id_from_reservation()

    def set_name(self):
        if not self.name:
            self.name = self.get_name_from_reservation()

    def get_instance_id_from_reservation(self):
        return self.reservation_info['Instances'][0]['InstanceId'] 

    def get_name_from_reservation(self):
        tags = self.reservation_info['Instances'][0]['Tags']
        return [tag['Value'] for tag in tags if tag['Key'] == 'Name'][0]



