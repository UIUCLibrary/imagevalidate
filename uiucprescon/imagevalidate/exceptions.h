//
// Created by Borchers, Henry Samuel on 9/7/18.
//

#ifndef OPENJPEGWRAPPER_EXCEPTIONS_H
#define OPENJPEGWRAPPER_EXCEPTIONS_H

#endif //OPENJPEGWRAPPER_EXCEPTIONS_H

#include <exception>
#include <sstream>
#include <utility>

class InvalidFileException: public std::exception{
    std::string error_message_;

public:
    explicit InvalidFileException(std::string filename): error_message_(std::move(filename)){};
    InvalidFileException(const std::string &filename, const std::string &msg){
        std::ostringstream error_message;

        error_message << filename;

        error_message << ": " << msg;
        error_message_ = error_message.str();
    };

    const char *what() const noexcept override{

        return error_message_.c_str();
    }

};