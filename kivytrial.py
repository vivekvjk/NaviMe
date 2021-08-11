from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
import time
allobj = []
import imagebox

def localize_objects(path):
    """Localize objects in the local image.

    Args:
    path: The path to the local file.
    """
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    with open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)

    objects = client.object_localization(
        image=image).localized_object_annotations

    print('Number of objects found: {}'.format(len(objects)))
    for object_ in objects:
        count = 0
        add = 1
        for element in allobj:
            for vertex in object_.bounding_poly.normalized_vertices:
                for vertex2 in  element.bounding_poly.normalized_vertices:
                    if vertex.x == vertex2.x and vertex.y == vertex2.y:
                        count+=1
                    if count == 3:
                        add = 0
                        break

                #print(' - ({}, {})'.format(vertex.x, vertex.y))
        if add == 1:
            allobj.append(object_)

        print('\n{} (confidence: {})'.format(object_.name, object_.score))
        print('Normalized bounding polygon vertices: ')
        for vertex in object_.bounding_poly.normalized_vertices:
            print(' - ({}, {})'.format(vertex.x, vertex.y))

def speak(text):
    # import speech_recognition as sr
    import os
    import random
    from gtts import gTTS
    language = 'en'
    myobj = gTTS(text=text, lang=language, slow=False)
    myobj.save("hello.mp3")
    os.system("mpg321 hello.mp3")

def drawbox (object_, image1):
    import imutils
    import cv2

    image = cv2.imread(image1)
    (h, w, d) = image.shape
    # print("width={}, height={}, depth={}".format(w, h, d))

    boxCoordinates = []

    # draw box around objects
    i = 0;
    for vertex in object_.bounding_poly.normalized_vertices:
        if(i ==0):
            boxCoordinates.append(vertex.x)
            boxCoordinates.append(vertex.y)

        elif(i ==2):
            boxCoordinates.append(vertex.x)
            boxCoordinates.append(vertex.y)
        i+=1
    j = 0;
    output = image.copy()
    # while (j < len(boxCoordinates)):
    x1 = int(w*boxCoordinates[j])
    y1 = int(h*boxCoordinates[j+1])
    x2 =  int(w*boxCoordinates[j+2])
    y2 = int(h*boxCoordinates[j+3])
    cv2.rectangle(output,(x1,y1), (x2,y2), (0, 0, 255), 2)
    j+=4
        # cv2.rectangle(output, (ULPointX, ULPointY), (LLPointX, LRPointY), (0, 0, 255), 2)
    cv2.imshow("Rectangle", output)
    cv2.waitKey(0)


var = ""
img = var
Builder.load_string('''
<CameraClick>:
    orientation: 'vertical'
    Camera:
        id: camera
        resolution: (2000, 1500)
        play: False
    ToggleButton:
        text: 'Play'
        on_press: camera.play = not camera.play
        size_hint_y: None
        height: '48dp'
    Button:
        text: 'Capture'
        size_hint_y: None
        height: '48dp'
        on_press: root.capture()
''')


class CameraClick(BoxLayout):
    def capture(self):
        '''
        Function to capture the images and give them the names
        according to their captured time and date.
        '''
        camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        var = "IMG_{}.png".format(timestr)
        camera.export_to_png(var)
        print(var)
        img = var
        localize_objects(img)

        print("printing")
        print(allobj)



        for element in allobj:
            drawbox(element, img)
            xval = 0.0
            count = 0
            for vertex in element.bounding_poly.normalized_vertices:
                    xval += vertex.x
                    if count ==2:
                        break
                    else:
                        count+=1


            xval =  xval/2
            leftorright = ""
            opp = ""
            if xval > 0.6:
                leftorright = "to your right"
                opp = "to your left"
            elif xval < 0.4:
                leftorright = "to your left"
                opp = "to your right"
            else:
                leftorright = "right in front of you"
                opp = "back"


            #calculate area
            x1= 0.0
            y1 = 0.0
            x2= 0.0
            y2 = 0.0
            i =0;
            for vector in element.bounding_poly.normalized_vertices:
                    # if xlength == 0.0:
                    #     xlength += vertex.x
                    # if xlength!= 0.0:
                    #     xlength -= vertex.x

                    # if ylength == 0.0:
                    #     ylength+=vertex.y
                    # if ylength!= 0.0:
                    #     ylength -= vertex.y
                    if i == 0:
                        x1=vector.x
                        y1=vector.y
                    if i==2:
                        x2 = vector.x
                        y2 = vector.y

                    i+=1

            area = (x2-x1)*(y2-y1)
            info = "There is a "+element.name +" occupying "+str((int(area*100))) + " percent of your view " + leftorright +". Please move "+opp + "."
            speak(info)



class TestCamera(App):

    def build(self):
        return CameraClick()


TestCamera().run()




# NOTE: GOOGLE_APPLICATION_CREDENTIALS needed from user's Google account
