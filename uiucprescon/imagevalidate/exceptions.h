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
    const std::string filename;
    std::string message;

public:
    explicit InvalidFileException(std::string filename):filename(std::move(filename)){};
    InvalidFileException(std::string filename, std::string msg):filename(std::move(filename)), message(std::move(msg)){};

    const char *what() const throw() override{
        std::ostringstream error_message;

        error_message << filename;

        if (!message.empty()){
            error_message << ": " << message;
        }

        return error_message.str().c_str();
    }

};