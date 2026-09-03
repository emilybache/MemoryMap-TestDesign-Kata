Memory Map Test Design Kata
===========================

Make the code and tests as readable as possible. 

The software needs to take a piece of memory of fixed size and allocate and de-allocate pieces of it. You can request to allocate various types, with some rules for where they can be allocated:

* Bool (1 Bit)      Alignment rule: can be allocated at any bit address
* Byte (8 Bits)     Alignment rule: must be allocated at a byte address
* Word (2\*8 Bits)   Alignment rule: must be allocated at an even byte address
* DWord (4\*8 Bits)  Alignment rule: must be allocated at an even byte address

## Example scenario:
The sketch below is from a domain expert, showing what should happen in a sample scenario. You begin with 10 bytes of empty memory, then allocate a DWord, a Byte, de-allocate the DWord, then allocate a Word. 

```
|0       1       2       3       4       5       6       7       8       9       |  Bytes
|01234567012345670123456701234567012345670123456701234567012345670123456701234567|  Bits
|--------------------------------------------------------------------------------|  Memory usage

Legend:
-------
b                                 = Bool  'b'  (1 Bit)
Bxxxxxxx                          = Byte  'B'  (8 Bits)
Wxxxxxxxxxxxxxxx                  = Word  'W'  (2*8 Bits)
Dxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  = DWord 'D'  (4*8 Bits)

Provide empty memory page of maximum 10 Bytes:
|0       1       2       3       4       5       6       7       8       9       |  Bytes
|01234567012345670123456701234567012345670123456701234567012345670123456701234567|  Bits
|--------------------------------------------------------------------------------|  Memory usage

Allocate A of type DWord
|0       1       2       3       4       5       6       7       8       9       |  Bytes
|01234567012345670123456701234567012345670123456701234567012345670123456701234567|  Bits
|Axxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx------------------------------------------------|  Memory usage

Allocate B of type Byte
|0       1       2       3       4       5       6       7       8       9       |  Bytes
|01234567012345670123456701234567012345670123456701234567012345670123456701234567|  Bits
|AxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxBxxxxxxx----------------------------------------|  Memory usage

Deallocate A
|0       1       2       3       4       5       6       7       8       9       |  Bytes
|01234567012345670123456701234567012345670123456701234567012345670123456701234567|  Bits
|--------------------------------Bxxxxxxx----------------------------------------|  Memory usage

Allocate C of type Word
|0       1       2       3       4       5       6       7       8       9       |  Bytes
|01234567012345670123456701234567012345670123456701234567012345670123456701234567|  Bits
|Cxxxxxxxxxxxxxxx----------------Bxxxxxxx----------------------------------------|  Memory usage
```

## Other interesting scenarios
* allocating overlapping pieces of memory (should not be allowed)
* allocating memory that doesn't fit into the available space (should not be allowed)
* memory is fragmented so there would be enough space for allocation if items were moved around. (should move items then allocate).
