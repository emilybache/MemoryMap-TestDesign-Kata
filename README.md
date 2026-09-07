Memory Map Test Design Kata
===========================

Make the code and tests as readable as possible. 

The software needs to take a piece of memory of fixed size and allocate and de-allocate pieces of it. You can request to allocate various types, with some rules for where they can be allocated.

## Example scenario
The sketch below is from a domain expert, showing what should happen in a sample scenario. You begin with 8 bytes of empty memory, then allocate a DWord, a Byte, de-allocate the DWord, then allocate a Word. Note: the spaces shown between bytes are not reflected on disk, they are included to make the diagrams easier to read for humans.

```
|0        1        2        3        4        5        6        7        |  Bytes
|01234567 01234567 01234567 01234567 01234567 01234567 01234567 01234567 |  Bits
|-------- -------- -------- -------- -------- -------- -------- -------- |  Memory usage

Legend:
-------
b                                    = Bool  'b'  (1 Bit)
Bbbbbbbb                             = Byte  'B'  (8 Bits)
Wwwwwwww wwwwwwww                    = Word  'W'  (2*8 Bits)
Dddddddd dddddddd dddddddd dddddddd  = DWord 'D'  (4*8 Bits)

Provide empty memory page of maximum 8 Bytes:
|0        1        2        3        4        5        6        7        |  Bytes
|01234567 01234567 01234567 01234567 01234567 01234567 01234567 01234567 |  Bits
|-------- -------- -------- -------- -------- -------- -------- -------- |  Memory usage

Allocate A of type DWord
|0        1        2        3        4        5        6        7        |  Bytes
|01234567 01234567 01234567 01234567 01234567 01234567 01234567 01234567 |  Bits
|Aaaaaaaa aaaaaaaa aaaaaaaa aaaaaaaa -------- -------- -------- -------- |  Memory usage

Allocate B of type Byte
|0        1        2        3        4        5        6        7        |  Bytes
|01234567 01234567 01234567 01234567 01234567 01234567 01234567 01234567 |  Bits
|Aaaaaaaa aaaaaaaa aaaaaaaa aaaaaaaa Bbbbbbbb -------- -------- -------- |  Memory usage

Deallocate A
|0        1        2        3        4        5        6        7        |  Bytes
|01234567 01234567 01234567 01234567 01234567 01234567 01234567 01234567 |  Bits
|-------- -------- -------- -------- Bbbbbbbb -------- -------- -------- |  Memory usage

Allocate C of type Word
|0        1        2        3        4        5        6        7        |  Bytes
|01234567 01234567 01234567 01234567 01234567 01234567 01234567 01234567 |  Bits
|Cccccccc cccccccc -------- -------- Bbbbbbbb -------- -------- -------- |  Memory usage
```

## Allocation rules
* Each memory allocation is contiguous, without gaps, and allocations may not overlap.
* Follow the alignment rules:
  * Bool (1 Bit)      Alignment rule: can be allocated at any bit address
  * Byte (8 Bits)     Alignment rule: must be allocated at a byte address
  * Anything larger than a Byte (eg a Word) must be allocated at an even byte address
* Use the lowest memory address where the allocation would fit. 
* If memory is fragmented so there would be enough space for an allocation if items were moved around, move items to make space, then allocate.

# Exercise Instructions
Two exercises - I suggest doing them on separate occasions, in this order.

## Compare different testing styles for this problem.
* Make a list of scenarios that need to be built and tested, based on the allocation rules.
* Work through the list and add tests for each scenario in both the 'classic' style and the 'approvals' style, following the example of the existing test.
* Don't forget to commit every time the tests are passing.
* When all the scenarios are implemented and working, review the tests for readability. Note down pros and cons of each kind. For example, how much test code is there? How easy is it to read? Do you think it will be easy to maintain when the requirements change?

## Assess diagnosability of different testing styles.
* Go to the 'sample_solution' branch where you have many scenarios implemented in both testing styles. Ensure all the tests pass. 
* There are 12 bugs hidden behind feature flags. We will use 6 to examine the 'classic' tests and the other 6 to examine the 'approval' tests. DO NOT look at the implementation code to find out what each bug is. That will spoil the fun!
* Enable one bug at a time. Based purely on the test failures, write bug reports explaining each problem. Examine odd bugs with a 'classic' test failure and even bugs with an 'approval' test failure, so you alternate which kind of test to use in your analysis.
* Discuss: How easy was it to diagnose each kind of test failure purely from the test failure message? Were either 'classic' or 'approval' style tests easier to diagnose? You can now look at the implementation code to find out if your bug reports were correct.
