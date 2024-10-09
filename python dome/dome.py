import FreeCAD as App
import Part, math

innerRadius = 20
outerRadius = 25
xyCount = 18
xyAngle = 360 / xyCount
xzCount = 9
xzAngle = math.pi / 2 / xzCount
n = 1
xyRotation = 0

def makeVoussoir():
	p1 = App.Vector(math.cos(xzAngle * (n-1)) * innerRadius, 0, math.sin(xzAngle * (n-1)) * innerRadius)
	p2 = App.Vector(math.cos(xzAngle * (n-1)) * outerRadius, 0, math.sin(xzAngle * (n-1)) * outerRadius)
	p3 = App.Vector(math.cos(xzAngle * (n-0.5)) * outerRadius, 0, math.sin(xzAngle * (n-0.5)) * outerRadius)
	p4 = App.Vector(math.cos(xzAngle * n) * outerRadius, 0, math.sin(xzAngle * n) * outerRadius)
	p5 = App.Vector(math.cos(xzAngle * n) * innerRadius, 0, math.sin(xzAngle * n) * innerRadius)
	p6 = App.Vector(math.cos(xzAngle * (n-0.5)) * innerRadius, 0, math.sin(xzAngle * (n-0.5)) * innerRadius)

	s1 = Part.LineSegment(p1, p2)
	a2 = Part.Arc(p2, p3, p4)
	s3 = Part.LineSegment(p4, p5)
	a4 = Part.Arc(p5, p6, p1)

	e1 = s1.toShape()
	e2 = a2.toShape()
	e3 = s3.toShape()
	e4 = a4.toShape()

	w = Part.Wire([e1, e2, e3, e4])

	f = Part.Face(w)

	o = App.Vector(0, 0, 0)
	z = App.Vector(0, 0, 1)
	voussoir = f.revolve(o, z, xyAngle)

	voussoir.rotate(o, z, xyRotation)

	return voussoir

while n < xzCount:
	while xyRotation < 360:
		v = makeVoussoir()
		Part.show(v)
		xyRotation += xyAngle
	n += 1
	if n % 2 == 0:
		xyRotation = xyAngle / 2
	else:
		xyRotation = 0