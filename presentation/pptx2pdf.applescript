on run argv
  set inPath to POSIX file (item 1 of argv)
  set outPath to POSIX file (item 2 of argv)
  tell application "Keynote"
    set theDoc to open inPath
    delay 3
    export theDoc to outPath as PDF
    close theDoc saving no
  end tell
end run
