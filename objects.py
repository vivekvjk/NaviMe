# NOTE: GOOGLE_APPLICATION_CREDENTIALS needed from user's Google account
allobj = []

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
        allobj.append(object_)
        print('\n{} (confidence: {})'.format(object_.name, object_.score))
        print('Normalized bounding polygon vertices: ')
        for vertex in object_.bounding_poly.normalized_vertices:
            print(' - ({}, {})'.format(vertex.x, vertex.y))


localize_objects("/Users/karenli/Desktop/codeday/trial.png")

print("printing")
print(allobj)

leftorright=[]
for element in allobj:
    xval = 0.0
   
    for vertex in element.bounding_poly.normalized_vertices:
            xval += vertex.x
            
            
    xval =  xval/2
    
    if xval > 0.5:
        leftorright.append("right")
    if xval < 0.5:
        leftorright.append("left")
    if xval == 0.5:
        leftorright.append("middle") 
    #calculate area
    xlength = 0.0
    ylength = 0.0
    for vertex in element.bounding_poly.normalized_vertices:
            if xlength == 0.0:
                xlength += vertex.x
            if xlength!= 0.0:
                xlength -= vertex.x
            
            if ylength == 0.0:
                ylength+=vertex.y
            if ylength!= 0.0:
                ylength -= vertex.y
    area = xlength*ylength
    
