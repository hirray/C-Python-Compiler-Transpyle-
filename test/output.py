global_counter = 100
uninitialized_int = None
uninitialized_int = 42
initialized_int = 10
initialized_int = initialized_int + uninitialized_int
pi = 3.14159
precise_val = 12345.67890123
letter = 'A'
message = list("Initial")
message[0] = 'B'
DAYS_IN_WEEK = 7
is_active = 1
target = [500]
ptr = target
ptr[0] = 600
x = 1
y = 2
z = 3
print("--- Variable Values ---")
print(f"Global: {global_counter}")
print(f"Integers: {uninitialized_int}, {initialized_int}")
print(f"Floats: {pi:.2f}, {precise_val:.8f}")
print(f"Char: {letter}, String: {''.join(message) if isinstance(message, list) else message}")
print(f"Constant: {DAYS_IN_WEEK}")
print(f"Boolean: {is_active}")
print(f"Pointer Value: {ptr[0]} (Target: {target[0]})")
print(f"Multi-decl: {x} {y} {z}")