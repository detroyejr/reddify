{ pkgs, ... }:

{
  name = "reddify";
  languages.python = {
    enable = true;
    package = pkgs.python3.withPackages(ps: with ps; [
      praw
      pushover-complete
      toml
    ]);
  };
  processes.run.exec = "python reddify.py";
}
