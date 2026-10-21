# anyPS Target Template: PlayStation 5

Direktori ini menyediakan kerangka kerja dasar (*boilerplate*) untuk membuat profil game PlayStation 5 baru di dalam repositori **anyPS**.

---

## Langkah Membuat Target PS5 Baru

1. Salin direktori `targets/ps5_template/` menjadi `targets/ps5_<game_id>/` (misal: `targets/ps5_demonsouls`).
2. Sesuaikan konfigurasi di `target.ini`:
   - `platform = ps5`
   - `game_id = <game_id>`
   - `title_id = <PPSAxxxxx>`
3. Kembangkan patch biner atau hooking di `ps5_patches.c`.
4. Kompilasi menggunakan CMake:
   ```bash
   cmake -B build -DPLATFORM=ps5 -DTARGET_GAME=<game_id>
   cmake --build build
   ```
