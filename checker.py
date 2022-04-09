"""
Checker classes
"""

import re

from abc import ABCMeta, abstractmethod
from maya import cmds
from maya.api import OpenMaya
from PySide2 import QtWidgets


if not cmds.pluginInfo("meshChecker", q=True, loaded=True):
    try:
        cmds.loadPlugin("meshChecker")
    except RuntimeError:
        cmds.warning("Failed to load meshChecker plugin")

if not cmds.pluginInfo("uvChecker", q=True, loaded=True):
    try:
        cmds.loadPlugin("uvChecker")
    except RuntimeError:
        cmds.warning("Failed to load uvChecker plugin")

if not cmds.pluginInfo("findUvOverlaps", q=True, loaded=True):
    try:
        cmds.loadPlugin("findUvOverlaps")
    except RuntimeError:
        cmds.warning("Failed to load uvOverlap checker plugin")


class Error(QtWidgets.QListWidgetItem):
    """ Custom error object """

    def __init__(self, fullPath, errors=None, parent=None):
        # type: (str, list) -> (None)
        super(Error, self).__init__(parent)
        self.components = errors
        self.longName = fullPath
        self.shortName = fullPath.split("|")[-1]

        self.setText(self.shortName)


class BaseChecker:
    """ Base abstract class for each checker """

    __metaclass__ = ABCMeta
    __category__ = ""
    __name__ = ""
    isWarning = False
    isEnabled = True
    isFixable = False

    def __init__(self):

        self.errors = []

    def __eq__(self, other):
        return self.name == self.name

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return (self.category < other.category)

    @abstractmethod
    def checkIt(self, objs, settings=None):
        """ Check method """

        pass

    @abstractmethod
    def fixIt(self):
        """ Fix method """

        pass

    @property
    def name(self):
        """ Label property """

        return self.__name__

    @property
    def category(self):
        return self.__category__


class TriangleChecker(BaseChecker):
    """ Triangle checker class """

    __name__ = "Triangles"
    __category__ = "Topology"
    isWarning = True

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)

        errorsDict = {}
        self.errors = []

        errs = cmds.checkMesh(obj, c=0)

        for e in errs:
            base, comp = e.split(".")

            if base in errorsDict:
                errorsDict[base].append(e)
            else:
                errorsDict[base] = [e]

        for err_key in errorsDict:
            components = errorsDict[err_key]
            errorObj = Error(err_key, errorsDict[err_key])
            self.errors.append(errorObj)

        return self.errors

    def fixIt(self):
        pass


class NgonChecker(BaseChecker):

    __name__ = "N-gons"
    __category__ = "Topology"

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)

        errorsDict = {}
        self.errors = []

        errs = cmds.checkMesh(obj, c=1)

        for e in errs:
            base, comp = e.split(".")

            if base in errorsDict:
                errorsDict[base].append(e)
            else:
                errorsDict[base] = [e]

        for err_key in errorsDict:
            components = errorsDict[err_key]
            errorObj = Error(err_key, errorsDict[err_key])
            self.errors.append(errorObj)

        return self.errors

    def fixIt(self):
        pass


class NonmanifoldEdgeChecker(BaseChecker):

    __name__ = "Nonmanifold Edges"
    __category__ = "Topology"

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)

        errorsDict = {}
        self.errors = []

        errs = cmds.checkMesh(obj, c=2)

        for e in errs:
            base, comp = e.split(".")

            if base in errorsDict:
                errorsDict[base].append(e)
            else:
                errorsDict[base] = [e]

        for err_key in errorsDict:
            components = errorsDict[err_key]
            errorObj = Error(err_key, errorsDict[err_key])
            self.errors.append(errorObj)

        return self.errors

    def fixIt(self):
        pass


class NonmanifoldVertexChecker(BaseChecker):

    __name__ = "Nonmanifold Vertices"
    __category__ = "Topology"

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)

        self.errors = []

        children = cmds.listRelatives(obj, fullPath=True, ad=True, type="mesh")

        for obj in children:
            try:
                errs = cmds.polyInfo(obj, nmv=True)
                if errs:
                    errorObj = Error(obj, errs)
                    self.errors.append(errorObj)
            except RuntimeError:
                pass

        return self.errors

    def fixIt(self):
        pass


class LaminaFaceChecker(BaseChecker):

    __name__ = "Lamina Faces"
    __category__ = "Topology"

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)

        errorsDict = {}
        self.errors = []

        errs = cmds.checkMesh(obj, c=3)

        for e in errs:
            base, comp = e.split(".")

            if base in errorsDict:
                errorsDict[base].append(e)
            else:
                errorsDict[base] = [e]

        for err_key in errorsDict:
            components = errorsDict[err_key]
            errorObj = Error(err_key, errorsDict[err_key])
            self.errors.append(errorObj)

        return self.errors

    def fixIt(self):
        pass


class BiValentFaceChecker(BaseChecker):

    __name__ = "Bi-valent Faces"
    __category__ = "Topology"

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)

        errorsDict = {}
        self.errors = []

        errs = cmds.checkMesh(obj, c=4)

        for e in errs:
            base, comp = e.split(".")

            if base in errorsDict:
                errorsDict[base].append(e)
            else:
                errorsDict[base] = [e]

        for err_key in errorsDict:
            components = errorsDict[err_key]
            errorObj = Error(err_key, errorsDict[err_key])
            self.errors.append(errorObj)

        return self.errors

    def fixIt(self):
        pass


class ZeroAreaFaceChecker(BaseChecker):

    __name__ = "Zero Area Faces"
    __category__ = "Topology"

    def checkIt(self, obj, settings):
        # type: (list) -> (list)

        mfa = settings.getSettings()['maxFaceArea']

        errorsDict = {}
        self.errors = []

        errs = cmds.checkMesh(obj, c=5, maxFaceArea=mfa)

        for e in errs:
            base, comp = e.split(".")

            if base in errorsDict:
                errorsDict[base].append(e)
            else:
                errorsDict[base] = [e]

        for err_key in errorsDict:
            components = errorsDict[err_key]
            errorObj = Error(err_key, errorsDict[err_key])
            self.errors.append(errorObj)

        return self.errors

    def fixIt(self):
        pass


class MeshBorderEdgeChecker(BaseChecker):

    __name__ = "Mesh Border Edges"
    isWarning = True
    __category__ = "Topology"

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)

        errorsDict = {}
        self.errors = []

        errs = cmds.checkMesh(obj, c=6)

        for e in errs:
            base, comp = e.split(".")

            if base in errorsDict:
                errorsDict[base].append(e)
            else:
                errorsDict[base] = [e]

        for err_key in errorsDict:
            components = errorsDict[err_key]
            errorObj = Error(err_key, errorsDict[err_key])
            self.errors.append(errorObj)

        return self.errors

    def fixIt(self):
        pass


class CreaseEdgeChecker(BaseChecker):

    __name__ = "Crease Edges"
    __category__ = "Topology"

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)

        errorsDict = {}
        self.errors = []

        errs = cmds.checkMesh(obj, c=7)

        for e in errs:
            base, comp = e.split(".")

            if base in errorsDict:
                errorsDict[base].append(e)
            else:
                errorsDict[base] = [e]

        for err_key in errorsDict:
            components = errorsDict[err_key]
            errorObj = Error(err_key, errorsDict[err_key])
            self.errors.append(errorObj)

        return self.errors

    def fixIt(self):
        pass


class ZeroLengthEdgeChecker(BaseChecker):

    __name__ = "Zero-length Edges"
    __category__ = "Topology"

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)

        errorsDict = {}
        self.errors = []

        errs = cmds.checkMesh(obj, c=8)

        for e in errs:
            base, comp = e.split(".")

            if base in errorsDict:
                errorsDict[base].append(e)
            else:
                errorsDict[base] = [e]

        for err_key in errorsDict:
            components = errorsDict[err_key]
            errorObj = Error(err_key, errorsDict[err_key])
            self.errors.append(errorObj)

        return self.errors

    def fixIt(self):
        pass


class VertexPntsChecker(BaseChecker):

    __name__ = "Vertex Pnts Attribute"
    __category__ = "Attribute"
    isFixable = True

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)

        self.errors = []

        errs = cmds.checkMesh(obj, c=9)

        for e in errs:
            errObj = Error(e)
            self.errors.append(errObj)

        return self.errors

    def fixIt(self):
        mSel = OpenMaya.MSelectionList()
        for n, e in enumerate(self.errors):
            if cmds.objExists(e.longName):
                obj = e.longName
                mSel.add(obj)
                try:
                    cmds.polyMoveVertex(
                        obj, lt=(0, 0, 0), nodeState=1, ch=False)
                except RuntimeError:
                    pass

class EmptyGeometryChecker(BaseChecker):

    __name__ = "Empty Geometry"
    __category__ = "Topology"
    isFixable = False

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)

        self.errors = []

        errs = cmds.checkMesh(obj, c=10)

        for e in errs:
            errObj = Error(e)
            self.errors.append(errObj)

        return self.errors

    def fixIt(self):
        pass


class NameChecker(BaseChecker):

    __name__ = "Name"
    __category__ = "Name"
    isEnabled = False

    def checkIt(self, objs, settings=None):
        # type: (list) -> (list)

        self.errors = []

        for obj in objs:
            try:
                pass
            except RuntimeError:
                pass

        return self.errors

    def fixIt(self):
        pass


class ShapeNameChecker(BaseChecker):

    __name__ = "ShapeName"
    __category__ = "Name"
    isFixable = True

    def checkIt(self, root, settings=None):
        # type: (list) -> (list)

        self.errors = []

        objs = cmds.listRelatives(root, ad=True, fullPath=True, type="transform") or []

        for obj in objs:
            shapes = cmds.listRelatives(
                obj, children=True, fullPath=True, shapes=True) or []
            if shapes:
                for shape in shapes:
                    isIntermediate = cmds.getAttr(
                        shape + ".intermediateObject")
                    if isIntermediate:
                        continue
                    shortName = obj.split("|")[-1]
                    shapeShortName = shape.split("|")[-1]

                    if shortName + "Shape" != shapeShortName:
                        err = Error(shape)
                        self.errors.append(err)

        return self.errors

    def fixIt(self):
        for e in self.errors:
            shape = e.longName
            parent = cmds.listRelatives(shape, parent=True, fullPath=False)[0]
            newShapeName = parent + "Shape"
            cmds.rename(shape, newShapeName)


class HistoryChecker(BaseChecker):

    __name__ = "History"
    __category__ = "Node"
    isEnabled = True
    isFixable = True

    def checkIt(self, root, settings=None):
        # type: (list) -> (list)

        self.errors = []

        objs = cmds.listRelatives(root, ad=True, fullPath=True, type="transform") or []

        for obj in objs:
            mesh = cmds.listRelatives(obj, children=True, type="mesh")
            if mesh is not None:
                for m in mesh:
                    inMesh = cmds.listConnections(m + ".inMesh", source=True)
                    if inMesh is not None:
                        err = Error(obj)
                        self.errors.append(err)

        return self.errors

    def fixIt(self):

        for e in self.errors:
            cmds.delete(e.longName, ch=True)


class TransformChecker(BaseChecker):

    __name__ = "Transform"
    __category__ = "Attribute"

    def checkIt(self, root, settings=None):
        # type: (list) -> (list)

        ignore = []

        self.errors = []

        identity = OpenMaya.MMatrix.kIdentity
        mSel = OpenMaya.MSelectionList()

        objs = cmds.listRelatives(root, ad=True, fullPath=True, type="transform") or []

        for n, i in enumerate(objs):
            mSel.add(i)
            dagPath = mSel.getDagPath(n)
            groupName = dagPath.fullPathName().split("|")[-1]
            if groupName in ignore:
                continue
            dagNode = OpenMaya.MFnDagNode(dagPath)
            transform = dagNode.transformationMatrix()
            if not transform == identity:
                errorObj = Error(i)
                self.errors.append(errorObj)

        return self.errors

    def fixIt(self):
        pass


class LockedTransformChecker(BaseChecker):

    __name__ = "Locked Transform"
    __category__ = "Attribute"
    isFixable = True

    def __init__(self):
        super(LockedTransformChecker, self).__init__()
        self.attrs = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]

    def checkIt(self, root, settings=None):
        # type: (list) -> (list)

        self.errors = []

        objs = cmds.listRelatives(root, ad=True, fullPath=True, type="transform") or []

        for obj in objs:
            try:
                for at in self.attrs:
                    isLocked = cmds.getAttr(obj + ".{}".format(at), lock=True)
                    if isLocked:
                        err = Error(obj)
                        self.errors.append(err)
                        break
            except RuntimeError:
                pass

        return self.errors

    def fixIt(self):
        for e in self.errors:
            for at in self.attrs:
                cmds.setAttr(e.longName + ".{}".format(at), lock=False)


class SmoothPreviewChecker(BaseChecker):

    __name__ = "Smooth Preview"
    __category__ = "Attribute"
    isFixable = True

    def checkIt(self, root, settings=None):
        # type: (list) -> (list)

        self.errors = []

        meshes = cmds.listRelatives(root, ad=True, fullPath=True, type="mesh") or []

        for mesh in meshes:
            isSmooth = cmds.getAttr(mesh + ".displaySmoothMesh")

            if isSmooth:
                err = Error(mesh)
                self.errors.append(err)

        return self.errors

    def fixIt(self):

        for e in self.errors:
            cmds.setAttr(e.longName + ".displaySmoothMesh", 0)


class KeyframeChecker(BaseChecker):

    __name__ = "Keyframe"
    __category__ = "Attribute"
    isFixable = True

    def checkIt(self, root, settings=None):
        # type: (list) -> (list)

        self.errors = []

        keyNodes = ["animCurveTU", "animCurveTA", "animCurveTL"]

        objs = cmds.listRelatives(root, ad=True, fullPath=True, type="transform") or []

        for i in objs:
            conns = cmds.listConnections(i, source=True)
            keys = []

            if conns is None:
                continue

            for c in conns:
                if cmds.objectType(c) in keyNodes:
                    keys.append(c)
            if keys:
                err = Error(i, keys)
                self.errors.append(err)

        return self.errors

    def fixIt(self):

        for e in self.errors:
            cmds.delete(e.components)


class UnusedVertexChecker(BaseChecker):
    """ Unused vertex checker class """

    __name__ = "Unused Vertices"
    __category__ = "Topology"

    def __init__(self):
        super(UnusedVertexChecker, self).__init__()

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)

        errorsDict = {}
        self.errors = []

        errs = cmds.checkMesh(obj, c=11)

        for e in errs:
            base, comp = e.split(".")

            if base in errorsDict:
                errorsDict[base].append(e)
            else:
                errorsDict[base] = [e]

        for err_key in errorsDict:
            components = errorsDict[err_key]
            errorObj = Error(err_key, errorsDict[err_key])
            self.errors.append(errorObj)

        return self.errors

    def fixIt(self):
        """ Unused vertices ARE fixable """

        pass


class IntermediateObjectChecker(BaseChecker):

    __name__ = "Intermediate Object"
    __category__ = "Node"
    isFixable = True

    def checkIt(self, root, settings=None):
        # type: (list) -> (list)

        self.errors = []

        meshes = cmds.listRelatives(root, ad=True, fullPath=True, type="mesh")

        for mesh in meshes:
            isIntermediate = cmds.getAttr(mesh + ".intermediateObject")
            if isIntermediate:
                err = Error(mesh)
                self.errors.append(err)

        return self.errors

    def fixIt(self):
        for e in self.errors:
            shape = e.longName

            if cmds.objExists(shape):
                parents = cmds.listRelatives(
                    shape, fullPath=True, parent=True) or []
                for i in parents:
                    # Delete history for parents
                    cmds.delete(i, ch=True)
                try:
                    cmds.delete(shape)
                except ValueError:
                    pass


class InstanceShapeChecker(BaseChecker):

    __name__ = "Instance Shape"
    __category__ = "Node"

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)

        self.errors = []

        errs = cmds.checkMesh(obj, c=12)

        for e in errs:
            errObj = Error(e)
            self.errors.append(errObj)

        return self.errors

    def fixIt(self):
        pass


class ConnectionChecker(BaseChecker):

    __name__ = "Connections"
    __category__ = "Node"

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)

        self.errors = []

        errs = cmds.checkMesh(obj, c=13)

        for e in errs:
            errObj = Error(e)
            self.errors.append(errObj)

        return self.errors

    def fixIt(self):
        pass


class DisplayLayerCheck(BaseChecker):

    __name__ = "Display layers"
    __category__ = "other"
    isFixable = True

    def checkIt(self, root, settings=None):
        # type: (list) -> (list)

        self.errors = []

        objs = cmds.listRelatives(root, ad=True, fullPath=True, type="transform") or []

        for obj in objs:
            layers = cmds.listConnections(obj + ".drawOverride") or []
            if layers:
                err = Error(obj, layers)
                self.errors.append(err)

        return self.errors

    def fixIt(self):

        for e in self.errors:
            layers = e.components
            node = e.longName
            for layer in layers:
                cmds.disconnectAttr(
                    layer + ".drawInfo", node + ".drawOverride")


class UnusedLayerChecker(BaseChecker):

    __name__ = "Unused layers"
    __category__ = "other"
    isFixable = True

    def checkIt(self, root, settings=None):
        # type: (list) -> (list)

        self.errors = []

        layers = cmds.ls(type="displayLayer")
        layers.remove("defaultLayer")
        for layer in layers:
            contents = cmds.editDisplayLayerMembers(
                layer, q=True, fullNames=True)
            if contents is None:
                err = Error(layer, [layer])
                self.errors.append(err)

        return self.errors

    def fixIt(self):
        for e in self.errors:
            try:
                cmds.delete(e.longName)
            except RuntimeError:
                pass


class Map1Checker(BaseChecker):

    __name__ = "UVSet to map1"
    __category__ = "UV"
    isFixable = True

    def checkIt(self, root, settings=None):
        # type: (list) -> (list)

        self.errors = []

        meshes = cmds.listRelatives(root, ad=True, fullPath=True, type="mesh") or []

        for mesh in meshes:
            curUVSet = cmds.polyUVSet(mesh, q=True, currentUVSet=True)[0]
            if curUVSet != "map1":
                err = Error(mesh)
                self.errors.append(err)

        return self.errors

    def fixIt(self):

        for e in self.errors:
            cmds.polyUVSet(e.longName, uvSet="map1", currentUVSet=True)


class NegativeUvChecker(BaseChecker):

    __name__ = "UVs in negative space"
    __category__ = "UV"

    def checkIt(self, root, settings=None):

        self.errors = []

        objs = cmds.listRelatives(root, ad=True, fullPath=True, type="transform") or []

        mSel = OpenMaya.MSelectionList()

        for obj in objs:
            mSel.add(obj)

        for i in range(mSel.length()):
            dagPath = mSel.getDagPath(i)
            try:
                dagPath.extendToShape()
                badUVs = []
                fnMesh = OpenMaya.MFnMesh(dagPath)
                uArray, vArray = fnMesh.getUVs()

                for index, uv in enumerate(zip(uArray, vArray)):
                    if uv[0] < 0 or uv[1] < 0:
                        fullPath = dagPath.fullPathName() + \
                            ".map[{}]".format(index)
                        badUVs.append(fullPath)
                if badUVs:
                    err = Error(dagPath.fullPathName(), badUVs)
                    self.errors.append(err)

            except RuntimeError:
                # Not mesh. Do no nothing
                pass

        return self.errors

    def fixIt(self):
        pass


class UdimIntersectionChecker(BaseChecker):

    __name__ = "UDIM intersection"
    __category__ = "UV"

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)
        
        self.errors = []

        errorsDict = {}

        errs = cmds.checkUV(obj, c=0)

        for e in errs:
            base, comp = e.split(".")

            if base in errorsDict:
                errorsDict[base].append(e)
            else:
                errorsDict[base] = [e]

        for err_key in errorsDict:
            components = errorsDict[err_key]
            errorObj = Error(err_key, errorsDict[err_key])
            self.errors.append(errorObj)

        return self.errors

    def fixIt(self):
        pass


class UnassignedUvChecker(BaseChecker):

    __name__ = "Unassigned UVs"
    __category__ = "UV"

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)
        
        self.errors = []

        errorsDict = {}

        errs = cmds.checkUV(obj, c=3)

        for e in errs:
            base, comp = e.split(".")

            if base in errorsDict:
                errorsDict[base].append(e)
            else:
                errorsDict[base] = [e]

        for err_key in errorsDict:
            components = errorsDict[err_key]
            errorObj = Error(err_key, errorsDict[err_key])
            self.errors.append(errorObj)

        return self.errors

    def fixIt(self):
        pass


class UnmappedPolygonFaceChecker(BaseChecker):

    __name__ = "Unmapped polygon faces"
    __category__ = "UV"

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)
        
        self.errors = []

        errorsDict = {}

        errs = cmds.checkUV(obj, c=1)

        for e in errs:
            base, comp = e.split(".")

            if base in errorsDict:
                errorsDict[base].append(e)
            else:
                errorsDict[base] = [e]

        for err_key in errorsDict:
            components = errorsDict[err_key]
            errorObj = Error(err_key, errorsDict[err_key])
            self.errors.append(errorObj)

        return self.errors

    def fixIt(self):
        pass


class ZeroAreaUVFaceChecker(BaseChecker):

    __name__ = "Zero area UV Faces"
    __category__ = "UV"

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)
        
        self.errors = []
        errorsDict = {}

        errs = cmds.checkUV(obj, c=2)

        for e in errs:
            base, comp = e.split(".")

            if base in errorsDict:
                errorsDict[base].append(e)
            else:
                errorsDict[base] = [e]

        for err_key in errorsDict:
            components = errorsDict[err_key]
            errorObj = Error(err_key, errorsDict[err_key])
            self.errors.append(errorObj)

        return self.errors

    def fixIt(self):
        pass


class ConcaveUVChecker(BaseChecker):

    __name__ = "Concave UV Faces"
    __category__ = "UV"

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)
        
        self.errors = []
        errorsDict = {}

        errs = cmds.checkUV(obj, c=5)

        for e in errs:
            base, comp = e.split(".")

            if base in errorsDict:
                errorsDict[base].append(e)
            else:
                errorsDict[base] = [e]

        for err_key in errorsDict:
            components = errorsDict[err_key]
            errorObj = Error(err_key, errorsDict[err_key])
            self.errors.append(errorObj)

        return self.errors

    def fixIt(self):
        pass


class ReversedUVChecker(BaseChecker):

    __name__ = "Reversed UV Faces"
    __category__ = "UV"
    isWarning = True

    def checkIt(self, obj, settings=None):
        # type: (list) -> (list)
        
        self.errors = []
        errorsDict = {}

        errs = cmds.checkUV(obj, c=6)

        for e in errs:
            base, comp = e.split(".")

            if base in errorsDict:
                errorsDict[base].append(e)
            else:
                errorsDict[base] = [e]

        for err_key in errorsDict:
            components = errorsDict[err_key]
            errorObj = Error(err_key, errorsDict[err_key])
            self.errors.append(errorObj)

        return self.errors

    def fixIt(self):
        pass


class UvOverlapChecker(BaseChecker):

    __name__ = "UV Overlaps"
    __category__ = "UV"
    isEnabled = False

    def checkIt(self, root, settings=None):

        self.errors = []

        objs = cmds.listRelatives(root, ad=True, fullPath=True, type="mesh") or []

        mSel = OpenMaya.MSelectionList()

        for obj in objs:
            mSel.add(obj)

        for i in range(mSel.length()):
            dagPath = mSel.getDagPath(i)
            try:
                dagPath.extendToShape()

            except RuntimeError:
                # Not mesh. Do no nothing
                pass

        return self.errors

    def fixIt(self):
        pass


class SelectionSetChecker(BaseChecker):

    __name__ = "Selection Sets"
    __category__ = "other"
    isFixable = True

    def getSets(self, path, typ):

        if typ == "transform":
            conns = cmds.listConnections(path + ".instObjGroups") or []
            return [i for i in conns if cmds.objectType(i) == "objectSet"]
        elif typ == "shape":
            conns = cmds.listConnections(
                path + ".instObjGroups.objectGroups") or []
            return [i for i in conns if cmds.objectType(i) == "objectSet"]
        else:
            pass

        return []

    def checkIt(self, root, settings=None):
        # type: (list) -> (list)

        self.errors = []
        objectSets = []
        ignore = ["modelPanel[0-9]ViewSelectedSet"]

        objs = cmds.listRelatives(root, ad=True, fullPath=True, type="transform") or []

        for obj in objs:
            shapes = cmds.listRelatives(
                obj, children=True, fullPath=True, shapes=True) or []

            for shape in shapes:
                objectSets.extend(self.getSets(shape, "shape"))

            objectSets.extend(self.getSets(obj, "transform"))

        objectSets = list(set(objectSets))

        for objSet in objectSets:
            for i in ignore:
                if re.match(i, objSet) is None:
                    err = Error(objSet)
                    self.errors.append(err)

        return self.errors

    def fixIt(self):
        for e in self.errors:
            try:
                cmds.delete(e.longName)
            except Exception:
                pass


class ColorSetChecker(BaseChecker):

    __name__ = "Color Sets"
    __category__ = "other"
    isFixable = True

    def checkIt(self, root, settings=None):
        # type: (list) -> (list)

        # Reset result
        self.errors = []

        objs = cmds.listRelatives(root, ad=True, fullPath=True, type="mesh") or []

        for obj in objs:
            try:
                allColorSets = cmds.polyColorSet(
                    obj, q=True, allColorSets=True)
                if allColorSets is None:
                    continue
                else:
                    err = Error(obj)
                    self.errors.append(err)
            except RuntimeError:
                pass

        return self.errors

    def fixIt(self):
        for i in self.errors:
            allSets = cmds.polyColorSet(
                i.longName, q=True, allColorSets=True) or []
            for s in allSets:
                cmds.polyColorSet(i.longName, delete=True, colorSet=s)


CHECKERS = [
    NameChecker,
    ShapeNameChecker,
    HistoryChecker,
    TransformChecker,
    LockedTransformChecker,
    SmoothPreviewChecker,
    KeyframeChecker,
    TriangleChecker,
    NgonChecker,
    NonmanifoldEdgeChecker,
    NonmanifoldVertexChecker,
    LaminaFaceChecker,
    BiValentFaceChecker,
    ZeroAreaFaceChecker,
    MeshBorderEdgeChecker,
    CreaseEdgeChecker,
    ZeroLengthEdgeChecker,
    VertexPntsChecker,
    EmptyGeometryChecker,
    UnusedVertexChecker,
    IntermediateObjectChecker,
    InstanceShapeChecker,
    ConnectionChecker,
    DisplayLayerCheck,
    UnusedLayerChecker,
    Map1Checker,
    NegativeUvChecker,
    UdimIntersectionChecker,
    UnassignedUvChecker,
    UnmappedPolygonFaceChecker,
    ZeroAreaUVFaceChecker,
    ConcaveUVChecker,
    ReversedUVChecker,
    UvOverlapChecker,
    SelectionSetChecker,
    ColorSetChecker]
