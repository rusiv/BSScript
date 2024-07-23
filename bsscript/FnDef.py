import re

class FnDef:
	TYPE_FUNCTION = 'function'
	TYPE_PROCEDURE = 'procedure'
	def __init__(self, callType, name, parameters = '', returnType = 'void'):		
		self.type = callType
		self.name = name
		self.returnType = returnType
		self.parameters = {}
		#todo: var параметры
		parameters = parameters.replace(' ', '')
		if (parameters):			
			for paramGroup in parameters.split(';'):
				matcher = re.search(r'(?P<names>(.*)):(?P<type>(.*))', paramGroup, flags = re.IGNORECASE)
				if matcher == None:
					continue
				matcherDict = matcher.groupdict()
				for paramName in matcherDict.get('names').split(','):
					self.parameters[paramName] = matcherDict.get('type')

	
	def toString(self):		
		params = ''
		for paramName in self.parameters:
			params = params + '  * @param ' + self.parameters[paramName] + ' ' + paramName + ' [description]\n'
		rtrn = '  * @return void\n'
		if self.type == FnDef.TYPE_FUNCTION:
			rtrn = '  * @return ' + self.returnType + ' [description]\n'
		return '{**\n' + \
			'  * [description]\n' + \
			params + \
			rtrn + \
		'*}'

