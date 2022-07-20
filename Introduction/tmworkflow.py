import Pyro5
import sys
sys.path.append('../..')
sys.path.append('..')
import models
from mupif import *
import mupif as mp
import logging

log = logging.getLogger()


class Example06(mp.Workflow):

    def __init__(self, metadata=None):
        """
        Initializes the workflow.
        """
        MD = {
            'Name': 'Thermo-mechanical stationary problem',
            'ID': 'Thermo-mechanical-1',
            'Description': 'stationary thermo-mechanical problem using finite elements on rectangular domain',
            # 'Dependencies' are generated automatically
            'Version_date': '1.0.0, Feb 2019',
            'Inputs': [
                    {
                        'Name': 'edge temperature',
                        'Type': 'mupif.Property',
                        'Required': False,
                        'Type_ID': 'mupif.DataID.PID_Temperature',
                        'Obj_ID': [
                            'Cauchy top',
                            'Cauchy bottom',
                            'Cauchy left',
                            'Cauchy right',
                            'Dirichlet top',
                            'Dirichlet bottom',
                            'Dirichlet left',
                            'Dirichlet right'
                        ],
                        'Units': 'K',
                        "Set_at": "timestep",
                        "ValueType": "Scalar"
                    }
                ],
            'Outputs': [
                {'Type': 'mupif.Field', 'Type_ID': 'mupif.DataID.FID_Temperature', 'Name': 'Temperature field',
                 'Description': 'Temperature field on 2D domain', 'Units': 'degC'},
                {'Type': 'mupif.Field', 'Type_ID': 'mupif.DataID.FID_Displacement', 'Name': 'Displacement field',
                 'Description': 'Displacement field on 2D domain', 'Units': 'm'}
            ],
            'Models': [
                {
                    'Name': 'thermal',
                    'Module': 'models',
                    'Class': 'ThermalModel'
                },
                {
                    'Name': 'mechanical',
                    'Module': 'models',
                    'Class': 'MechanicalModel'
                }
            ]
        }
        super().__init__(metadata=MD)
        self.updateMetadata(metadata)

    def initialize(self, workdir='', metadata=None, validateMetaData=True, **kwargs):
        super().initialize(workdir=workdir, metadata=metadata, validateMetaData=validateMetaData, **kwargs)

        thermalInputFile = mp.PyroFile(filename='inputT.in', mode="rb", dataID=mp.DataID.ID_InputFile)
        # self.daemon.register(thermalInputFile)
        self.getModel('thermal').set(thermalInputFile)

        mechanicalInputFile = mp.PyroFile(filename='inputM.in', mode="rb", dataID=mp.DataID.ID_InputFile)
        # self.daemon.register(mechanicalInputFile)
        self.getModel('mechanical').set(mechanicalInputFile)

    def solveStep(self, istep, stageID=0, runInBackground=False):
        self.getModel('thermal').solveStep(istep, stageID, runInBackground)
        self.getModel('mechanical').set(self.getModel('thermal').get(DataID.FID_Temperature, istep.getTime()))
        self.getModel('mechanical').solveStep(istep, stageID, runInBackground)

    def get(self, objectTypeID, time=None, objectID=""):
        if objectTypeID == DataID.FID_Temperature:
            return self.getModel('thermal').get(objectTypeID, time, objectID)
        elif objectTypeID == DataID.FID_Displacement:
            return self.getModel('mechanical').get(objectTypeID, time, objectID)
        else:
            raise apierror.APIError('Unknown field ID')
    def set(self, property, objectID=0):
        if property.getPropertyID() == mp.DataID.PID_Temperature:
            self.getModel('thermal').set(property, objectID)
        else:
            raise mp.apierror.APIError('Unknown property ID')

    def getCriticalTimeStep(self):
        return 1*mp.U.s

    def getApplicationSignature(self):
        return "Example06 workflow 1.0"

    def getAPIVersion(self):
        return "1.0"

