"""
Specialization of USD variants classes in Katana.
It's written on Python to be able to use complex UI and PySide.
"""

# Copyright 2017 Rodeo FX. All rights reserved.

import walterWidgets
from UI4.FormMaster import KatanaFactory
from UI4.Manifest import QT4FormWidgets
from UI4.Widgets import ToolbarButton
from UI4.Util import IconManager
from UI4.Manifest import QtGui
from walterUSDExtern import WalterUSDExtern


class VariantAction(walterWidgets.BaseVariantAction):
    def __init__(self, primPath, index,
                 variantName, variantSetName, isSelected, menu):
        super(VariantAction, self).__init__(
            primPath, index, variantName,
            variantSetName, isSelected, menu)

    def _setVariantValue(self):
        """Implementation of walterWidgets.BaseVariantAction."""

        walterUSDExtern = self.menu.parent.walterUSDExtern
        variant = walterUSDExtern.setVariantUsd(
            self.primPath, self.variantSetName, self.variantName)

        arrayParameterPolicy = self.menu.parent.parent.getValuePolicy()
        arrayParameterPolicy.getArrayChild(
            self.index).setValue(variant)


class VariantSetMenu(walterWidgets.BaseVariantSetMenu):
    def __init__(self, primPath, index, variantSetName, parent):
        super(VariantSetMenu, self).__init__(
            primPath, index, variantSetName, parent)

    def _constructVariantAction(self, primPath, index,
                                variantName, variantSetName, isSelected):
        """Implementation of walterWidgets.BaseVariantSetMenu."""
        return VariantAction(primPath, index, variantName,
                             variantSetName, isSelected, self)


class VariantsMenu(walterWidgets.BaseVariantsMenu):
    """Menu for editing USD variants."""

    def __init__(self, parent):
        super(VariantsMenu, self).__init__(parent)
        self.walterUSDExtern = WalterUSDExtern()

    def _getVariantList(self):
        """Implementation of walterWidgets.BaseVariantsMenu."""
        self.walterUSDExtern.setIdentifier(self.nodePath)

        # Set the current variants from Katana parameters
        arrayParameterPolicy = self.parent.getValuePolicy()
        arraySize = arrayParameterPolicy.getArraySize()[0]
        for i in range(0, arraySize):
            child = arrayParameterPolicy.getArrayChild(i)
            childValue = child.getValue()
            self.walterUSDExtern.setVariantUsdFlat(childValue)

        # Resize the parameters
        self.walterUSDExtern.extractVariantsUsd()
        arrayParameterPolicy.setArraySize(
            [self.walterUSDExtern.getPrimsCount(), 1])

        return self.walterUSDExtern.getVariantsUsd().split('|')

    def _createMenu(self, primPath, index, variantSetName):
        """Implementation of walterWidgets.BaseVariantsMenu."""
        return VariantSetMenu(
            primPath, index, variantSetName, self)


class WalterVariantsToolbar(QT4FormWidgets.BaseValueFormWidget):

    def _buildControlWidget(self, layout):
        """Called when FormWidget needs a container for control widgets."""

        self.variantsMenu = VariantsMenu(self)

        action = QtGui.QAction("Variants", self)
        action.triggered.connect(self.__showVariantsMenu)

        self.__variantButton = ToolbarButton(
            "Variants", self, IconManager.GetPixmap('Icons/plug24.png'),
            None, None, None, False, False, None, None, None, None,
            action)

        layout.addWidget(self.__variantButton)

    def __showVariantsMenu(self):
        nodePath = self.getValuePolicy().getNode().getParameter(
            'abcAsset').getValue(0.0)

        if self.variantsMenu.reset(nodePath):
            self.variantsMenu.exec_(QtGui.QCursor.pos())


KatanaFactory.RegisterPluginWidget(
    "walterVariantsToolbar", WalterVariantsToolbar)
