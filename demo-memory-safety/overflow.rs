// The same logic in Rust: the copy is bounds-checked, so it cannot corrupt is_admin.
struct Session { username: [u8; 8], is_admin: i32 }

fn main() {
    let input = std::env::args().nth(1).unwrap_or("guest".into());
    let mut s = Session { username: [0; 8], is_admin: 0 };
    // copy_from_slice panics if the lengths differ - no silent overflow
    s.username[..input.len()].copy_from_slice(input.as_bytes());
    println!("is_admin={}", s.is_admin);
}
