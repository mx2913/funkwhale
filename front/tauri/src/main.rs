// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use color_eyre::Result;

fn main() -> Result<()> {
    color_eyre::install()?;

    funkwhale_lib::run();

    Ok(())
}
