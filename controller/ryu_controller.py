from configs import settings
from controller.apis.ryuapi import RyuApi


class RyuController:
    """
    Use this class to communicate with the Ryu SDN-Controller
    """
    def __init__(self):
        self.api = RyuApi()
