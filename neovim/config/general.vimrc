" Filetype-based indentation
if has('filetype')
  filetype indent plugin on
endif

" Use system clipboard
" https://vim.fandom.com/wiki/Accessing_the_system_clipboard
set clipboard=unnamedplus

" For vim-devicons
set encoding=UTF-8

" Enable mouse support in terminal
set mouse=a

" Enable line numbers
set number

" Drop vi support
set nocompatible

" Set statusline to indicate insert or normal mode
set showmode showcmd

" Search settings
set hlsearch    " highlight matches
set incsearch   " incremental searching
set ignorecase  " searches are case insensitive...
set smartcase   " ... unless they contain at least one capital letter

" Enable syntax highlighting
if has('syntax')
  syntax on
endif
