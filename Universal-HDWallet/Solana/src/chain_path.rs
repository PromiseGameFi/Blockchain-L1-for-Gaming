use crate::KeyIndex;
use std::borrow::Cow;
use std::fmt;

const MASTER_SYMBOL: &str = "m";
const HARDENED_SYMBOLS: [&str; 2] = ["H", "'"];
const SEPARATOR: char = '/';

#[derive(Clone, Debug, Copy, PartialEq, Eq)]
pub enum Error {
    Invalid,
    Blank,
    KeyIndexOutOfRange,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ChainPath<'a> {
    path: Cow<'a, str>,
}

impl<'a> ChainPath<'a> {
    pub fn new<S>(path: S) -> Self
    where
        S: Into<Cow<'a, str>>,
    {
        Self { path: path.into() }
    }

    /// An SubPath iterator over the ChainPath from Root to child keys.
    pub fn iter(&self) -> impl Iterator<Item = Result<SubPath, Error>> + '_ {
        Iter(self.path.split_terminator(SEPARATOR))
    }

    pub fn into_string(self) -> String {
        self.path.into()
    }

    /// Convert ChainPath to &str represent format
    fn to_string(&self) -> &str {
        &self.path
    }
}

#[derive(Debug, PartialEq, Eq)]
pub enum SubPath {
    Root,
    Child(KeyIndex),
}

pub struct Iter<'a, I: Iterator<Item = &'a str>>(I);

impl<'a, I: Iterator<Item = &'a str>> Iterator for Iter<'a, I> {
    type Item = Result<SubPath, Error>;

    fn next(&mut self) -> Option<Self::Item> {
        self.0.next().map(|sub_path| {
            if sub_path == MASTER_SYMBOL {
                return Ok(SubPath::Root);
            }
            if sub_path.is_empty() {
                return Err(Error::Blank);
            }
            let last_char = &sub_path[(sub_path.len() - 1)..];
            let is_hardened = HARDENED_SYMBOLS.contains(&last_char);
            let key_index = {
                let key_index_result = if is_hardened {
                    sub_path[..sub_path.len() - 1]
                        .parse::<u32>()
                        .map_err(|_| Error::Invalid)
                        .and_then(|index| {
                            KeyIndex::hardened_from_normalize_index(index)
                                .map_err(|_| Error::KeyIndexOutOfRange)
                        })
                } else {
                    sub_path[..]
                        .parse::<u32>()
                        .map_err(|_| Error::Invalid)
                        .and_then(|index| {
                            KeyIndex::from_index(index).map_err(|_| Error::KeyIndexOutOfRange)
                        })
                };
                key_index_result?
            };
            Ok(SubPath::Child(key_index))
        })
    }
}

impl<'a> From<String> for ChainPath<'a> {
    fn from(path: String) -> Self {
        ChainPath::new(path)
    }
}

impl<'a> From<&'a str> for ChainPath<'a> {
    fn from(path: &'a str) -> Self {
        ChainPath::new(path)
    }
}

impl fmt::Display for ChainPath<'_> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}", self.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    

    #[test]
    fn test_chain_path_new() {
        // new from string slice
        assert_eq!("m/1", ChainPath::new("m/1").to_string());
        // new from a runtime String
        assert_eq!("m/1", ChainPath::new(String::from("m/1")).to_string());
    }
}
