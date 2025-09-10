
#This project was made as an exercise in learning the mathematics behind how basic 3D rendering works
#The program uses the default console to draw images, utilizing an array of characters order based on how much space they take to shade objects
#The code was actively written and changed during the learning process, and as such it features less than optimal implementations.

#I tried not to use libraries related to 3D rendering and instead implement everything in base python for the sake of the exercise.
#this means the program is quite slow, as it is not well optimized for 3D graphical rendering.

#This program implements (at least primitively):
    #Simple 3D object format using python arrays for triangles and meshes
    #Converting points from world space to camera space, and then to screen space
    #Scene shading based on triangle surface normals relative to global light direction vector
    #Correct triangle drawing order using a depth buffer that stores the per pixel depth of everything on the screen
    #live mesh rotation
    
#CONTROLS --------------------------------------------------
    #Camera: The camera can be panned up, down, left, and right using the arrow keys
    #Movement: You can move the camera horizontally using the WASD keys, and vertically using left-shift and space
    #Remove: You can remove an object you are actively looking ay by pressing c


import math
import os
import keyboard

keyboard.press('f11')


#Function for normalizing a vector
def normalize(vec):
    magnitude = math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)
    vec[0]/=magnitude
    vec[1]/=magnitude
    vec[2]/=magnitude


#Class to represent a 3x3 matrix. Accepts 3 vectors representing the matrix rows during creation
class matrix3x3:
    def __init__(self, v1, v2, v3):
        self.matrix = [[],[],[]]
        self.matrix[0] = v1
        self.matrix[1] = v2
        self.matrix[2] = v3
    #sets new values for the matrix rows
    def updateMatrix(self, v1, v2, v3):
        self.matrix[0] = v1
        self.matrix[1] = v2
        self.matrix[2] = v3
    #function for multiplying matrix by a given vector. Returns the resulting vector
    def vectorMatrix(self, vec3):
        return [self.matrix[0][0] * vec3[0] + self.matrix[1][0] * vec3[1] + self.matrix[2][0] * vec3[2],self.matrix[0][1] * vec3[0] + self.matrix[1][1] * vec3[1] + self.matrix[2][1] * vec3[2] , self.matrix[0][2] * vec3[0] + self.matrix[1][2] * vec3[1] + self.matrix[2][2] * vec3[2]]


#class to represent the camera in 3D space
class camera:
    def __init__(self) -> None:
        self.fov = math.pi/2
        self.fovVert = math.pi/2
        self.pos = [0,0,0]
        self.angleUp = 0
        self.angleRight = 0
        self.near = 0.1
        self.far = 1000
        self.lookAtObj = None
        self.lookAtDepth = 999
    def move(self, x,y,z):
        self.pos[0] += x
        self.pos[1] += y
        self.pos[2] += z


#class to represent a triangle. takes three vertices represented as arrays of length 3
class triangle:
    def __init__(self, v1, v2, v3):
        self.values = [v1, v2, v3]


class obj:
    def __init__(self, triList, position):
       self.tris = []
       self.relativeTris = []
       self.rotationSide = 0
       self.rotationUp = 0
       self.pos = position

       self.yAxisMat = matrix3x3([math.cos(self.rotationSide), 0, -math.sin(self.rotationSide)] , [0, 1, 0] , [math.sin(self.rotationSide), 0  , math.cos(self.rotationSide)])
       self.xAxisMat = matrix3x3([1, 0, 0] , [0, math.cos(self.rotationUp), math.sin(self.rotationUp)] , [0, -math.sin(self.rotationUp)  , math.cos(self.rotationUp)])

       for tri in triList:
         self.tris.append(tri)
       self.updateMesh()
    def updateMesh(self):
        self.relativeTris.clear()

        self.yAxisMat.updateMatrix([math.cos(self.rotationSide), 0, -math.sin(self.rotationSide)] , [0, 1, 0] , [math.sin(self.rotationSide), 0  , math.cos(self.rotationSide)])
        self.xAxisMat.updateMatrix([1, 0, 0] , [0, math.cos(self.rotationUp), math.sin(self.rotationUp)] , [0, -math.sin(self.rotationUp)  , math.cos(self.rotationUp)])

        for tri in self.tris:
            newP1 = [tri.values[0][0], tri.values[0][1], tri.values[0][2]]
            newP2 = [tri.values[1][0], tri.values[1][1], tri.values[1][2]]
            newP3 = [tri.values[2][0], tri.values[2][1], tri.values[2][2]]

            newP1 = self.yAxisMat.vectorMatrix(newP1)
            newP1 = self.xAxisMat.vectorMatrix(newP1)

            newP2 = self.yAxisMat.vectorMatrix(newP2)
            newP2 = self.xAxisMat.vectorMatrix(newP2)

            newP3 = self.yAxisMat.vectorMatrix(newP3)
            newP3 = self.xAxisMat.vectorMatrix(newP3)
            

            newP1[0] += self.pos[0]
            newP1[1] += self.pos[1]
            newP1[2] += self.pos[2]

            newP2[0] += self.pos[0]
            newP2[1] += self.pos[1]
            newP2[2] += self.pos[2]

            newP3[0] += self.pos[0]
            newP3[1] += self.pos[1]
            newP3[2] += self.pos[2]


            self.relativeTris.append(triangle(newP1, newP2, newP3))


## CLASSES ABOVE FOR WHAT I NEED IN THE PROJECT ###


screen = []
depthBuffer = []
xWidth = 0
yWidth = 0
lightDirection = [-.3, 1, .2]
normalize(lightDirection)

shadingList = "`.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{CfI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@"
cam = camera()

## GLOBAL VARIABLES FOR THE SCENE ##

yAxisMatrix =  matrix3x3([math.cos(cam.angleRight), 0, -math.sin(cam.angleRight)] , [0, 1, 0] , [math.sin(cam.angleRight), 0  , math.cos(cam.angleRight)])
xAxisMatrix =  matrix3x3([1, 0, 0] , [0, math.cos(cam.angleUp), math.sin(cam.angleUp)] , [0, -math.sin(cam.angleUp)  , math.cos(cam.angleUp)])


## CREATE THE MATRICES FOR ROTATION 


def createScreen(x,y):
    global xWidth, yWidth
    for i in range(y):
        screen.append([])
        depthBuffer.append([])
    xWidth = x
    yWidth = y
def refreshScreen():
    for row in screen:
        list.clear(row)
        for i in range(xWidth):
            row.append(" ")
    for row in depthBuffer:
        list.clear(row)
        for i in range(xWidth):
            row.append(1000)  

## FUNCTIONS FOR CREATING AND REFRESHING THE SCREEN LISTS ##

def printScreen():
    os.system('cls')
    print("-"*xWidth)
    for row in screen:
        print("|" + "".join(row)+"|")
    print("-"*xWidth)
## PRINTS THE SCREEN ##
 #############################################################################################

def pointToCameraSpace(cameraObj, pointObj):
    newPoint = [pointObj[0] - cameraObj.pos[0], pointObj[1] - cameraObj.pos[1], pointObj[2] - cameraObj.pos[2]]
    

    newPoint = yAxisMatrix.vectorMatrix(newPoint)
    newPoint = xAxisMatrix.vectorMatrix(newPoint)

    
    
    return newPoint

def pointToScreenSpace(cameraObj, pointObj):
    newPoint = [pointObj[0] , pointObj[1], pointObj[2]]
    newPoint = [(pointObj[0]/(pointObj[2] * math.tan(cameraObj.fov/2)) + 1)/2, (pointObj[1]/(pointObj[2] * math.tan(cameraObj.fovVert/2))+1/2), ((pointObj[2] * cameraObj.far)/(cameraObj.far - cameraObj.near)- ( cameraObj.far*cameraObj.near/(cameraObj.far-cameraObj.near)  ) )/pointObj[2]]
    return newPoint

##FUNCTIONS FOR MANIPULATING A POINT AROUND A CAMERA##

def triArea(x1, y1, x2, y2, x3, y3):
     return (1/2) * (x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2))



 ## GET TRIANGLE AREA ##

def pointInTriangle(vec, p1, p2, p3):
    totalArea = abs(triArea(p1.values[0], p1.values[1],p2.values[0], p2.values[1],p3.values[0], p3.values[1]))
    tri1 = abs(triArea(p1.values[0], p1.values[1],p2.values[0], p2.values[1],vec.values[0], vec.values[1]))
    tri2 = abs(triArea(p1.values[0], p1.values[1],vec.values[0], vec.values[1],p3.values[0], p3.values[1]))
    tri3 = abs(triArea(vec.values[0], vec.values[1],p2.values[0], p2.values[1],p3.values[0], p3.values[1]))
    difference = abs((tri1 + tri2 + tri3) - totalArea)




    if difference <= 0.000000000000001:
        return True
    return False


def pointInTriangle2(vec, p1, p2, p3):


    
    
    #return  (det(  [subtract(p2, p1), subtract(vec, p1)]  )[0] > 0 and det(  [subtract(p3, p2), subtract(vec, p2)]  )[0] > 0 and det([subtract(p1, p3), subtract(vec, p3)])[0] > 0 )
    
    return  (p2[0] - p1[0])*(vec[1]-p1[1]) - (p2[1]-p1[1])*(vec[0]-p1[0]) > 0 and (p3[0] - p2[0])*(vec[1]-p2[1]) - (p3[1] - p2[1])*(vec[0] - p2[0]) > 0 and (p1[0] - p3[0])*(vec[1] - p3[1]) - (p1[1] - p3[1])*(vec[0] - p3[0]) > 0
    

## CHECKS IF A POINT IS IN A GIVEN TRIANGLE ##
timeDepth = 0
timeTriangle = 0
timeOther = 0

def pointDepth(vec, p1, p2, p3, y, x, ob):
    

    totalArea = abs(triArea(p1[0], p1[1],p2[0], p2[1],p3[0], p3[1])) + .00000000001
    depth = abs(triArea(vec[0], vec[1],p2[0], p2[1],p3[0], p3[1]))/totalArea * p1[2] + abs(triArea(p1[0], p1[1],vec[0], vec[1],p3[0], p3[1]))/totalArea * p2[2] + abs(triArea(p1[0], p1[1],p2[0], p2[1],vec[0], vec[1]))/totalArea * p3[2]
    if depth < depthBuffer[y][x]:
        depthBuffer[y][x] = depth
        if y == math.floor(yWidth/2) and x == math.floor(xWidth/2):
            cam.lookAtObj = ob
        
        return depth
    else:
        
        return False

## FINDS DEPTH OF A POINT ##

def pointAtZ(point1, point2, z):
    xDifference = point2[0] - point1[0]
    yDifference = point2[1] - point1[1]
    zDifference = point2[2] - point1[2]
    DistTraveled = z-point1[2]
    xAddition = xDifference/zDifference*DistTraveled
    yAddition = yDifference/zDifference*DistTraveled
    return [point1[0]+xAddition, point1[1]+yAddition, z]

##Find point between 2 points at given z value

def crossProd(v1, v2, v3):
    line1 = [v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]]
    line2 = [v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]]
    normalize(line1)
    normalize(line2)
    val1 = (line1[1]*line2[2]) - (line1[2]*line2[1]) 
    val2 = (line1[2]*line2[0]) - (line1[0]*line2[2]) 
    val3 = (line1[0]*line2[1]) - (line1[1]*line2[0])
    cross = [-val1,-val2,-val3]
    normalize(cross)
    return cross
## CROSS PRODUCT


def dotProd(v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1]  + v1[2]*v2[2]

##DOT PROD

triangleCheck = 0
DepthCHeck = 0


def drawTriangle(tri, obj):
    global initaltime
    global triangleCheck
    global DepthCHeck
    
    p1 =  pointToCameraSpace(cam, tri.values[0] )
    p2 =  pointToCameraSpace(cam, tri.values[1] ) 
    p3 =  pointToCameraSpace(cam, tri.values[2] ) 

    z1 = p1[2]
    z2 = p2[2]
    z3 = p3[2]


    behindList = []
    frontList = []
    if z1 < cam.near and z2 < cam.near and z3 < cam.near:
        return
    if z1 < cam.near:
        behindList.append(p1)
    else:
        frontList.append(p1)
    if z2 < cam.near:
        behindList.append(p2)
    else:
        frontList.append(p2)
    if z3 < cam.near:
        behindList.append(p3)
    else:
        frontList.append(p3)


    crossVec = crossProd(tri.values[0], tri.values[1], tri.values[2])

    if len(behindList) == 2:
        np1 = pointAtZ(behindList[0], frontList[0], cam.near)
        np2 = pointAtZ(behindList[1], frontList[0], cam.near)
        drawTriangleCamSpace(np1, np2, frontList[0], crossVec, obj)
        drawTriangleCamSpace(frontList[0], np2, np1, crossVec, obj)
        return
    if len(behindList) == 1:
        np1 = pointAtZ(behindList[0], frontList[0], cam.near)
        np2 = pointAtZ(behindList[0], frontList[1], cam.near)


        drawTriangleCamSpace(np1, np2, frontList[1], crossVec, obj)
        drawTriangleCamSpace( frontList[1], np2, np1, crossVec, obj)

        drawTriangleCamSpace(frontList[0], frontList[1], np2,  crossVec, obj)
        drawTriangleCamSpace( np2, frontList[1], frontList[0],  crossVec, obj)

        drawTriangleCamSpace(frontList[0], frontList[1], np1,  crossVec, obj)
        drawTriangleCamSpace( np1, frontList[1], frontList[0],  crossVec, obj)


        return
    drawTriangleCamSpace(p1,p2,p3,crossVec, obj)


    


###DRAW TRIANGLE 1


def drawTriangleCamSpace(p1, p2, p3, crossVec, obj):
    global screen

    p1 =  pointToScreenSpace(cam, p1)
    p2 =  pointToScreenSpace(cam, p2)
    p3 =  pointToScreenSpace(cam, p3)

    selector = math.floor(    dotProd(crossVec, lightDirection)  *  (len(shadingList)-1)/2   + len(shadingList)/2    )
    if selector < 0:
        selector = 0
    character = shadingList[selector]
    screen = [[character if pointInTriangle2([v/xWidth, 1 - i/yWidth], p1, p2, p3)  and  pointDepth([v/xWidth, 1 - i/yWidth, 1], p1, p2, p3, i, v, obj) != False else screen[i][v]  for v in range(xWidth) ] for i in range(yWidth)]



def drawObj(obj):
    for tri in obj.relativeTris:
        drawTriangle(tri, obj)



##############################
def generateSquare(pos, width):
     tri1 = triangle([-width,-width,-width], [width, -width, -width], [width, width, -width])
     tri2 = triangle([width, width, -width], [-width, width, -width], [-width,-width,-width])
    ## FRONT FACE
     tri3 = triangle([width, -width, -width], [width, -width, width], [width, width, width])
     tri4 = triangle([width, width, width], [width, width, -width], [width, -width, -width])
    ## RIGHT FACE
     tri5 = triangle([width,-width,width], [-width, -width, width], [-width,width,width])
     tri6 = triangle([-width,width,width], [width, width, width], [width,-width,width])
    ## BACK FACE
     tri7 = triangle([-width, -width, width], [-width,-width,-width], [-width, width, -width])
     tri8 = triangle([-width,width,-width], [-width, width, width], [-width,-width,width])
    ## LEFT FACE
     tri9 = triangle([-width, width, -width], [width, width, -width], [width, width, width])
     tri10 = triangle([width,width,width], [-width,width,width],[-width,width,-width])
    ##TOP FACE
     tri11 = triangle([width, -width, width], [width, -width, -width], [-width, -width, -width])
     tri12 = triangle([-width,-width,-width],[-width,-width,width], [width,-width,width], )     

    ## BOTTOM FACE
     return obj([tri1, tri2, tri3, tri4, tri5, tri6, tri7, tri8, tri9, tri10, tri11, tri12], pos)

def generateRect(pos, length, height, width, rotationX=0, rotationY=0):
     tri1 = triangle([-width,-height,-length], [width, -height, -length], [width, height, -length])
     tri2 = triangle([width, height, -length], [-width, height, -length], [-width,-height,-length])
    ## FRONT FACE
     tri3 = triangle([width, -height, -length], [width, -height, length], [width, height, length])
     tri4 = triangle([width, height, length], [width, height, -length], [width, -height, -length])
    ## RIGHT FACE
     tri5 = triangle([width,-height,length], [-width, -height, length], [-width,height,length])
     tri6 = triangle([-width,height,length], [width, height, length], [width,-height,length])
    ## BACK FACE
     tri7 = triangle([-width, -height, length], [-width,-height,-length], [-width, height, -length])
     tri8 = triangle([-width,height,-length], [-width, height, length], [-width,-height,length])
    ## LEFT FACE
     tri9 = triangle([-width, height, -length], [width, height, -length], [width, height, length])
     tri10 = triangle([width,height,length], [-width,height,length],[-width,height,-length])
    ##TOP FACE
     tri11 = triangle([width, -height, length], [width, -height, -length], [-width, -height, -length])
     tri12 = triangle([-width,-height,-length],[-width,-height, length], [width,-height,length], )   
     newObject = obj([tri1, tri2, tri3, tri4, tri5, tri6, tri7, tri8, tri9, tri10, tri11, tri12], pos)
     newObject.rotationSide = rotationY
     newObject.rotationUp = rotationX
     objects.append(newObject)

####CODE FOR GENERATING SHAPES
createScreen(200, 50)

cam.pos[2] = -10
square = generateSquare([-10,0,0], 2)
#objects = [square, ]#square2, square3, square4]
objects = []
objects.append(square)
def generateGrid(n, w):
    offset1=0
    for i in range(n):
        offset2=0
        for i in range(n):
            newObject = generateSquare([offset2, -2*w, offset1], w)
            objects.append(newObject)
            offset2 += 2*w
        offset1 += 2*w
    
generateGrid(1, 15)


t = 0
def renderStep():
    global screen
    global t
    t += .1
    refreshScreen()
    
    square.rotationSide = t/1.5
    square.rotationUp = t/1.5
    square.pos[1] = math.sin(t/1.5) * 3
    square.updateMesh()

    yAxisMatrix.updateMatrix([math.cos(cam.angleRight), 0, -math.sin(cam.angleRight)] , [0, 1, 0] , [math.sin(cam.angleRight), 0  , math.cos(cam.angleRight)])
    xAxisMatrix.updateMatrix([1, 0, 0] , [0, math.cos(cam.angleUp), math.sin(cam.angleUp)] , [0, -math.sin(cam.angleUp)  , math.cos(cam.angleUp)])
   

    cam.lookAtObj = None
    cam.lookAtDepth = 999

    
    for s in objects:
        drawObj(s)
    screen[math.floor(yWidth/2)][math.floor(xWidth/2)] = '\033[31m' + "@" + '\033[0m'
    screen[math.floor(yWidth/2)][math.floor(xWidth/2)-1] = '\033[31m' + "@" + '\033[0m'
    screen[math.floor(yWidth/2)+1][math.floor(xWidth/2)] = '\033[31m' + "@" + '\033[0m'
    screen[math.floor(yWidth/2)-1][math.floor(xWidth/2)] = '\033[31m' + "@" + '\033[0m'
    screen[math.floor(yWidth/2)][math.floor(xWidth/2)+1] = '\033[31m' + "@" + '\033[0m'
    #######################################################




    #######################################################
    printScreen()

    print(timeDepth, timeTriangle)


##HAPPENS EVERY FRAME
while True:
    forward = math.cos(cam.angleRight)
    side = math.sin(cam.angleRight)

    if t > 1000:
        break
    if keyboard.is_pressed("w"):
        cam.move(-side,0,forward)
    if keyboard.is_pressed("S"):
        cam.move(side,0,-forward)
    if keyboard.is_pressed("A"):
        cam.move(-forward, 0, -side)
    if keyboard.is_pressed("D"):
        cam.move(forward, 0, side)
    if keyboard.is_pressed(" "):
        cam.move(0,1,0)
    if keyboard.is_pressed("shift"):
        cam.move(0,-1,0)
    if keyboard.is_pressed("left arrow"):
        cam.angleRight += .06
        
    if keyboard.is_pressed("right arrow"):
        cam.angleRight -= .06

    
    if keyboard.is_pressed("up arrow"):
        cam.angleUp += .1
    if keyboard.is_pressed("down arrow"):
        cam.angleUp -= .1

    if keyboard.is_pressed("C"):
        
        if cam.lookAtObj != None:
            objects.remove(cam.lookAtObj)

    if cam.angleUp > math.pi/2:
        cam.angleUp = math.pi/2
    if cam.angleUp < -math.pi/2:
        cam.angleUp = -math.pi/2

    if cam.angleRight > math.pi*2:
        cam.angleRight -= math.pi*2
    if cam.angleRight < 0:
        cam.angleRight += math.pi*2

    
    print(cam.lookAtObj)
    renderStep()
