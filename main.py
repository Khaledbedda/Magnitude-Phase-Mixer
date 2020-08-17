from PyQt5 import QtWidgets
from mainWindow import Ui_MainWindow
import sys
from PyQt5.QtGui import QIcon, QPalette, QColor , QPixmap , QImage
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QMainWindow
import numpy as np
import matplotlib.pyplot as plt
from scipy import fftpack
import matplotlib as mtlp
from popup import Ui_Popup
import logging 

logging.basicConfig(filename="logging.log", 
                    format='%(asctime)s %(message)s', 
                    filemode='w') 

logger=logging.getLogger() 
  
#Setting the threshold of logger to DEBUG 
logger.setLevel(logging.DEBUG) 

class Component(): 
    def __init__(self, image = []): 
         self.image = image
         self.im_fft = fftpack.fft2(self.image) 
         self.mag= np.abs(self.im_fft)
         self.ph =  np.exp(1j*np.angle(self.im_fft))
         self.real = np.real(self.im_fft)
         self.im = 1j*np.imag(self.im_fft)
         self.select = ""
         self.comp=[]
          
      
    # getter method 
    def get_image(self): 
        return self.image 
      
    # setter method 
    def set_image(self, x): 
        self.image = x 

    def mix(self, image : 'Component' , comp1= "" ,comp2= "" , mode = "" , gain1 = 0.1 , gain2 = 0.1 ):
        if mode == "real_im" :
            imgCombined = np.real(np.fft.ifft2(  (self.get_comp(comp1)*gain1) + (image.get_comp(comp2)*gain2 )  )  )
            return imgCombined 
        elif mode == "mag_phase" :   
            imgCombined = np.real(np.fft.ifft2(    np.multiply(gain1* self.get_comp(comp1)  , gain2* image.get_comp(comp2))        ))
            return imgCombined


    def get_comp(self , selection ="") :
        if selection == "ft magnitude" : 
            return self.mag
        elif selection == "ft phase" : 
            return self.ph
        elif selection == "ft real" :
            return self.real
        elif selection == "ft imaginary"  :
            return self.im
        elif selection =="uniform magnitude" : 
            return np.ones(np.shape(self.mag))
        elif selection=="uniform phase": 
             return np.zeros(np.shape(self.ph))   

    def get_magnitude(self): 
        return self.mag

    def get_phase(self): 
         return self.ph


class fileBrowser():
    def __init__(self):
        self.path = ""

    def getFilePath(self):
        filename = QFileDialog.getOpenFileName(
            None, 'Load Signal', "*.png;;" "*.jpg")
        self.path = filename[0]
        return self.path


class ApplicationWindow(QtWidgets.QMainWindow , Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(ApplicationWindow, self).__init__(*args, **kwargs)
       # self.ui = Ui_MainWindow()
        self.setupUi(self)
        self.f= 0
        self.gain1 = 1 
        self.gain2 = 1
        self.menubar.triggered.connect(
            self.open_img)
        self.component = []
        self.componentmix = []
        self.comp1=""
        self.comp2=""
        self.mode = ""
        self.image_1= []
        self.image_2= []
        self.ui_popup = Ui_Popup()
        self.comboBox.activated.connect(
            self.setflag )
        self.comboBox.activated.connect(
            self.select_component )
        self.comboBox_3.activated.connect(
            self.resetflag )
        self.comboBox_3.activated.connect(
            self.select_component )
        self.comboBox_5.activated.connect(
            self.update_comp )
        self.comboBox_5.activated.connect(
            self.updtate_mode )
        self.comboBox_6.activated.connect(
            self.updtate_mode )
        self.comboBox_6.activated.connect(
            self.update_comp )
        self.horizontalSlider.valueChanged.connect(self.sliderupdate)
        self.horizontalSlider_2.valueChanged.connect(self.sliderupdate)
        #self.horizontalSlider_2.valueChanged.connect(self.sliderupdate)
        self.comboBox_2.activated.connect(self.display_mix)


    def updtate_mode(self):
        temp =  self.comboBox_5.currentText().lower()
        if temp == "ft real" or temp =="ft imaginary" :
            logger.info("mode changed from"+ self.mode +"to real_im")
            self.mode = "real_im"
        elif temp == "ft magnitude" or temp =="ft phase" or temp =="uniform magnitude" or temp =="uniform phase" : 
            logger.info("mode changed from"+ self.mode +"to mag_phase")
            self.mode = "mag_phase"    

    def display_mix(self):
        self.componentmix.append(self.comboBox_2.currentText().lower())
        temp = self.componentmix.pop()
        dis = self.mix()
        if np.any(dis) :
            if np.max(dis) > 1 : 
                dis = dis / np.max(dis)
            if temp == "output1" : 
                plt.imsave('output1.png', abs(dis))
                self.label_5.setPixmap(QPixmap('output1.png'))
                logger.info("Display mix of " +self.comboBox_5.currentText().lower() +" from " +self.comboBox_4.currentText().lower() +" with ratio " + str(self.gain1) +
                 " and "+self.comboBox_6.currentText().lower() +" from " +self.comboBox_7.currentText().lower() +" with ratio "+ str(self.gain1) +" on output 1" )
            elif temp == "output2" : 
                plt.imsave('output2.png', abs(dis))
                self.label_6.setPixmap(QPixmap('output2.png'))
                logger.info("Display mix of " +self.comboBox_5.currentText().lower() +" from " +self.comboBox_4.currentText().lower() +" with ratio " + str(self.gain1) +
                 " and "+self.comboBox_6.currentText().lower() +" from " +self.comboBox_7.currentText().lower() +" with ratio " + str(self.gain1)+" on output 2 " )

    def update_comp(self) : 
        self.comp1 = self.comboBox_5.currentText().lower()
        self.comp2 = self.comboBox_6.currentText().lower()
        logger.info(" component 1 selected is "+ self.comp1 + " and component 2 is " + self.comp2)


    def mix(self) : 

        self.component.append(self.comboBox_4.currentText().lower())
        temp1 = self.component.pop()
        self.component.append(self.comboBox_7.currentText().lower())
        temp2 = self.component.pop()

        if temp1 == "img1" : 
            if temp2 == "img1" :
                if np.any(self.image_1) : 
                    output = self.img_1.mix(self.img_1 , self.comp1 , self.comp2 , self.mode, self.gain1 , self.gain2)  
                else : 
                    logger.warning("Component selected doesn't exist") 
            elif temp2== "img2" :
                if np.any(self.image_1) and  np.any(self.image_2): 
                  output = self.img_1.mix(self.img_2 , self.comp1 , self.comp2 ,self.mode, self.gain1 , self.gain2)
                else : 
                    logger.warning("Component selected doesn't exist")   
        if temp1 == "img2" : 
            if temp2 == "img1" :
                if np.any(self.image_1) and  np.any(self.image_2):
                    output = self.img_2.mix(self.img_1 , self.comp1 , self.comp2, self.mode , self.gain1 , self.gain2)   
                else : 
                    logger.warning("Component selected doesn't exist") 
            elif temp2== "img2" :
                if np.any(self.image_2) : 
                    output = self.img_2.mix(self.img_2 , self.comp1 , self.comp2 , self.mode, self.gain1 , self.gain2)
                else : 
                    logger.warning("Component selected doesn't exist")                

        return output    

    
    def sliderupdate(self):
    
        self.gain1= self.horizontalSlider.value() / 100.0
        self.gain2 = self.horizontalSlider_2.value() / 100.0
        self.label_7.setText(str(self.gain1))
        self.label_8.setText(str(self.gain2))

    def setflag(self):
        self.f = 0 
    def resetflag(self):
        self.f = 1    

    def open_img(self):

        browser = fileBrowser()
        path = browser.getFilePath()

        if path:
            if self.label_2.pixmap() is None : 
               self.label_2.setPixmap(QPixmap(path))
               self.image_1 = plt.imread(path)
               self.image_1 =  self.image_1 / np.max( self.image_1)
               self.img_1 = Component(self.image_1)
               logger.info("OPenning image1 from path" + path)

            elif self.label_3.pixmap() is None :
               self.label_3.setPixmap(QPixmap(path))
               self.image_2 = plt.imread(path)
               self.image_2 =  self.image_2 / np.max( self.image_2)
               self.img_2 = Component(self.image_2) 
               logger.info("OPenning image2 from path" + path)
               if np.size(self.image_1) != np.size(self.image_2) : 
                self.popup()
                logger.warning("The two images doesn't have the same size")
        

          
    def select_component(self):
        if self.f == 0 :
            if np.any(self.image_1) :
                self.image = self.img_1
                dis_label = self.label
                self.component.append(self.comboBox.currentText().lower())
                temp = self.component.pop()
                logger.info("Display "+ temp+" of image 1")
            else : 
                logger.warning("Image 1 doesn't exist")    
        elif self.f == 1 : 
            if np.any(self.image_2) :
                self.image = self.img_2
                dis_label = self.label_4
                self.component.append(self.comboBox_3.currentText().lower())
                temp = self.component.pop()
                logger.info("Display "+ temp+" of image 2")
            else : 
                  logger.warning("Image 2 doesn't exist") 

        self.dis_imag = np.real(np.fft.ifft2(self.image.get_comp(temp)))
        if np.any(self.dis_imag) : 
            if np.max(self.dis_imag) > 1 :
                self.dis_imag = self.dis_imag / np.max(self.dis_imag)
            plt.imsave("comp.png", abs(self.dis_imag))
            dis_label.setPixmap(QPixmap('comp.png'))


    def popup(self):
        self.popup = QtWidgets.QMainWindow()
        self.ui_popup.setupUi(self.popup)
        self.popup.show()
 
        


def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()

    app.setStyle("Fusion")

    # Fusion dark palette from https://gist.github.com/QuantumCD/6245215.
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 0, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    app.setStyleSheet(
        "QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

    application.show()
    app.exec_()


if __name__ == "__main__":
    main()
