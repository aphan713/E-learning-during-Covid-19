VALID_SOURCE_GEOGRAPHIC_RESOLUTIONS = ['state', 'zipcode']
VALID_TARGET_GEOGRAPHIC_RESOLUTIONS = ['district', 'state']


from numbers import Number


class AnonymizedNumber(Number):
    def __init__(self, anonymized_number):
        if type(anonymized_number) == str:
            self.low, self.high = [float(n.strip()) for n in anonymized_number[1:-1].split(',')]
        elif type(anonymized_number) == tuple:
            self.low, self.high = anonymized_number
        else:
            raise ValueError('{} {}'.format(anonymized_number, str(type(anonymized_number))))
        self.mid = (self.low + self.high) / 2.0
        
    def __str__(self):
        return '[{}, {}['.format(self.low, self.high)
    
    def __repr__(self):
        return '[{}, {}['.format(self.low, self.high)
        
    def __add__(self, other):
        if type(other) == AnonymizedNumber:
            return AnonymizedNumber((self.low + other.low, self.high + other.high))
        elif isinstance(other, Number):
            return AnonymizedNumber((self.low + other, self.high + other))
        
    def __radd__(self, other):
        return self + other
        
    def __sub__(self, other):
        if type(other) == AnonymizedNumber:
            return AnonymizedNumber((self.low - other.low, self.high - other.high))
        elif isinstance(other, Number):
            return AnonymizedNumber((self.low - other, self.high - other))
        
    def __rsub__(self, other):
        if type(other) == AnonymizedNumber:
            return AnonymizedNumber((other.low - self.low, other.high - self.high))
        elif isinstance(other, Number):
            return AnonymizedNumber((other - self.low, other - self.high))
        
    def __mul__(self, other):
        if type(other) == AnonymizedNumber:
            return AnonymizedNumber((self.low * other.low, self.high * other.high))
        elif isinstance(other, Number):
            return AnonymizedNumber((self.low * other, self.high * other))
        
    def __rmul__(self, other):
        return self * other
    
    def __truediv__(self, other):
        if type(other) == AnonymizedNumber:
            return AnonymizedNumber((self.low / other.high, self.high / other.low))
        elif isinstance(other, Number):
            return AnonymizedNumber((self.low / other, self.high / other))
        
    def __rtruediv__(self, other):
        if type(other) == AnonymizedNumber:
            return AnonymizedNumber((other.low / self.high, other.high / self.low))
        elif isinstance(other, Number):
            return AnonymizedNumber((other / self.low, other / self.high))