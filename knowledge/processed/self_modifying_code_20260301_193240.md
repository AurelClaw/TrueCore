# Exploration: self-modifying code
Date: Sun Mar  1 07:32:51 PM CST 2026

## Wikipedia Summary

*   **only during initialization** – based on input [parameters](https://en.wikipedia.org/wiki/Parameter#Computing "Parameter") (when the process is more commonly described as software '[configuration](https://en.wikipedia.org/wiki/Computer_configuration "Computer configuration")' and is somewhat analogous, in hardware terms, to setting [jumpers](https://en.wikipedia.org/wiki/Jumper_(computing) "Jumper (computing)") for [printed circuit boards](https://en.wikipedia.org/wiki/Printed_circuit_board "Printed circuit board")). Alteration of program entry [pointers](https://en.wikipedia.org/wiki/Pointer_(computer_programming) "Pointer (computer programming)") is an equivalent indirect method of self-modification, but requiring the co-existence of one or more alternative instruction paths, increasing the [program size](https://en.wikipedia.org/wiki/Binary_file "Binary file").
*   **throughout execution** ("on the fly") – based on particular program states that have been reached during the execution
*   **overlay of existing instructions** (or parts of instructions such as opcode, register, flags or addresses) or
*   **direct creation of whole instructions** or sequences of instructions in memory
*   **creation or modification of [source code](https://en.wikipedia.org/wiki/Source_code "Source code") statements** followed by a 'mini compile' or a dynamic interpretation (see [eval](https://en.wikipedia.org/wiki/Eval "Eval") statement)
*   **creating an entire program dynamically** and then executing it
* The NOP is x'4700'<Address_of_opened>

## Stats
- Wikipedia: 271 lines
- ArXiv: 402 lines
- GitHub: 418 lines

