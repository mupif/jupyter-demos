import sys
sys.path.append('.')
import models
from mupif import *
import mupif as mp
import time
import logging

log = logging.getLogger()

# prototype of workflow implementation of stationary thermo-mechanical solver
class tmworkflow(mp.workflow.Workflow):

    def __init__(self, metadata={}):
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
                        'Type_ID': 'mupif.PropertyID.PID_Temperature',
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
                        'Units': 'K' 
                    }
                ],
            'Outputs': [
                {'Type': 'mupif.Field', 'Type_ID': 'mupif.FieldID.FID_Temperature', 'Name': 'Temperature field',
                 'Description': 'Temperature field on 2D domain', 'Units': 'degC'},
                {'Type': 'mupif.Field', 'Type_ID': 'mupif.FieldID.FID_Displacement', 'Name': 'Displacement field',
                 'Description': 'Displacement field on 2D domain', 'Units': 'm'}
            ]
        }
        super().__init__(metadata=MD)
        self.updateMetadata(metadata)

        self.thermalSolver = models.ThermalModel()
        self.mechanicalSolver = models.MechanicalModel()

        self.registerModel(self.thermalSolver, 'thermal')
        self.registerModel(self.mechanicalSolver, 'mechanical')

    def initialize(self, file='', workdir='', targetTime=0*mp.Q.s, metadata={}, validateMetaData=True):
        super().initialize(file=file, workdir=workdir, targetTime=targetTime, metadata=metadata,
                                          validateMetaData=validateMetaData)

        passingMD = {
            'Execution': {
                'ID': self.getMetadata('Execution.ID'),
                'Use_case_ID': self.getMetadata('Execution.Use_case_ID'),
                'Task_ID': self.getMetadata('Execution.Task_ID')
            }
        }

        self.thermalSolver.initialize('inputT.in', '.', metadata=passingMD)
        self.mechanicalSolver.initialize('inputM.in', '.', metadata=passingMD)
        #self.mechanicalSolver.printMetadata(nonEmpty=False)

    def solveStep(self, istep, stageID=0, runInBackground=False):
        self.thermalSolver.solveStep(istep, stageID, runInBackground)
        self.mechanicalSolver.setField(self.thermalSolver.getField(mp.FieldID.FID_Temperature, istep.getTime()))
        self.mechanicalSolver.solveStep(istep, stageID, runInBackground)

    def getField(self, fieldID, time, objectID=0):
        if fieldID == mp.FieldID.FID_Temperature:
            return self.thermalSolver.getField(fieldID, time, objectID)
        elif fieldID == mp.FieldID.FID_Displacement:
            return self.mechanicalSolver.getField(fieldID, time, objectID)
        else:
            raise mp.apierror.APIError('Unknown field ID')
    def setProperty(self, property, objectID=0):
        if property.getPropertyID() == mp.PropertyID.PID_Temperature:
            self.thermalSolver.setProperty(property, objectID)
        else:
            raise mp.apierror.APIError('Unknown property ID')

    def getCriticalTimeStep(self):
        return 1*mp.Q.s

    def terminate(self):
        self.thermalSolver.terminate()
        self.mechanicalSolver.terminate()
        super().terminate()

    def getApplicationSignature(self):
        return "TM workflow 1.0"

    def getAPIVersion(self):
        return "1.0"

