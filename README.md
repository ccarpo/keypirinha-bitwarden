# Keypirinha Plugin: bitwarden

This is bitwarden, a plugin for the
[Keypirinha](http://keypirinha.com) launcher.

When bitwarden CLI is setup and serves an local API you can use Keypirinha to find your credentials and copy username, password, the on time token (TOTP) in your clipboard or open the (first) URL belonging to that record


## Prerequisits

* You need to have the bitwarden CLI installed either 
   * Here: https://bitwarden.com/de-de/download/#downloads-command-line-interface
   * Or with winget: `winget install Bitwarden.CLI`
   * Or with chocolatey: `choco install bitwarden-cli`
* You need to login with `bw login` and save your login token in a system variable `BW_SESSION`
* You need to start `bw serve` so that the local API is available


## Download

The latest `.keypirinha-package` file can be downloaded at https://github.com/ccarpo/keypirinha-bitwarden/releases


## Install

Once the `bitwarden.keypirinha-package` file is installed,
move it to the `InstalledPackage` folder located at:

* `Keypirinha\portable\Profile\InstalledPackages` in **Portable mode**
* **Or** `%APPDATA%\Keypirinha\InstalledPackages` in **Installed mode** (the
  final path would look like
  `C:\Users\%USERNAME%\AppData\Roaming\Keypirinha\InstalledPackages`)


## Usage

Configure if you want to use the slower more secure method ("dynamic") or the fast but insecure method ("static") in the configuration file.
* `dynamic` makes an API query as you type at least three letters in the search box and returns the resuluts
* `static` queries all items ins your bitwarden vault when the catalog is scanned and returns results instantly from the catalog but with the drawback that all your secrets are in the keypirinha catalog.


## Change Log

There is an inital release now. But still some ideas to implement.

### v0.5

* Initial release with `dynamic` and `static` options


## Ideas to implement

- [ ] Lock/Unlock Vault
- [ ] Start `bw serve` on plugin start in the background
- [ ] Get notes from an item
- [ ] Generate username or password
- [ ] Make a BW_SESSSION variable in the Keypirinha config


## License

This package is distributed under the terms of the MIT license.


## Credits

Thanks for Bitwarden for this great Passwordmanager and Keypirinha for that magnificent launcher.


## Contribute

1. Check for open issues or open a fresh issue to start a discussion around a
   feature idea or a bug.
2. Fork this repository on GitHub to start making your changes to the **dev**
   branch.
3. Send a pull request.
4. Add yourself to the *Contributors* section below (or create it if needed)!
