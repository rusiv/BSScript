import os
from .BLSItem import BLSItem

WHITE = 0
GREY = 1
BLACK = 2

class Graph:
	vertexes = []
	shortNameIndexList = []
	
	def addVertex(self, vertex):
		self.vertexes.append(vertex)
		self.shortNameIndexList.append(vertex.shortName)

	def getVertexIndexByName(self, name):
		for i in range(len(self.vertexes)):
			if self.vertexes[i].name == name:
				return i
		return None

	def getVertexIndexByShortName(self, shorName):
		try:			
			return self.shortNameIndexList.index(shorName)
		except Exception:
			return None

	def getVertexByIndex(self, index):
		return self.vertexes[index]

class Vertex:
	def __init__(self, path, name, shortName):
		self.path = path
		self.name = name
		self.fullPath = path + '\\' + name
		self.shortName = shortName
		self.cycles = []
		
		self.color = WHITE
		self.edges = [];

class Dependencer:
	graph = Graph()
	blsDublicates = []
	__chain = []
	cycles = []
	compileOrder = []

	def __init__(self, blsFolderPath, onBlsComplete = None):
		self.missingFiles = []
		self.folder = blsFolderPath
		self.onBlsComplete = onBlsComplete
		self.buildGraph()
		self.buildEdges()

	def buildGraph(self):
		bllList = []

		for root, dirs, files in os.walk(self.folder):
			for name in files:
				if name.upper().endswith('.BLS'):
					nameWOExt = name[:name.rfind('.')].lower();

					if nameWOExt in bllList:
						if self.blsDublicates.count(nameWOExt) == 0:
							self.blsDublicates.append(nameWOExt)
					else:
						bllList.append(nameWOExt);
						
						vertex = Vertex(root.lower(), name.lower(), nameWOExt)
						self.graph.addVertex(vertex)

	def buildEdges(self):
		for vertex in self.graph.vertexes:
			dependences = BLSItem(vertex.fullPath, self.folder).dependence			
			if dependences:
				for dependence in dependences:
					dependence = dependence.lower()
					vertexIndex = self.graph.getVertexIndexByShortName(dependence)
					if vertexIndex != None:
						vertex.edges.append(vertexIndex)
					else:
						if dependence not in self.missingFiles:
							self.missingFiles.append(dependence)

	def getCycles(self):
		if self.blsDublicates:
			raise Exception('Duplicates detected: ' + ', '.join(self.blsDublicates))

		for vertex in self.graph.vertexes:
			self.dfs(vertex)

		return self.cycles

	def dfs(self, vertex):
		if vertex.color == BLACK:
			return None
		self.__chain.append(vertex.name)
		vertex.color = GREY	
		for key in vertex.edges:
			vertex2 = self.graph.getVertexByIndex(key)
			if vertex2.color == WHITE:
				self.dfs(vertex2)
			elif vertex2.color == GREY:				
				vertex.cycles.append(self.__chain)
				self.cycles.append(' -> '.join(self.__chain) + ' -> ' + vertex2.name)
				#break
		vertex.color = BLACK
		if self.onBlsComplete:
			self.onBlsComplete(vertex)
		self.__chain.pop()
		self.compileOrder.append(vertex.fullPath)

	def getOrder(self):
		return self.compileOrder
	
	def getVertexByPath(self, blsFullPath):
		for vertex in self.graph.vertexes:
			if vertex.fullPath.upper() == blsFullPath.upper():
				return vertex;