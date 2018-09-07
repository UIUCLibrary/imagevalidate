//
// Created by Borchers, Henry Samuel on 9/7/18.
//

#ifndef OPENJPEGWRAPPER_EXCEPTIONS_H
#define OPENJPEGWRAPPER_EXCEPTIONS_H

#endif //OPENJPEGWRAPPER_EXCEPTIONS_H

#include <exception>
#include <sstream>

class InvalidFileException: public std::exception{
    const std::string filename;
    std::string message;

public:
    InvalidFileException(const std::string &filename):filename(filename){};
    InvalidFileException(const std::string &filename, const std::string &msg):filename(filename), message(msg){};

    virtual const char *what() const throw(){
        std::ostringstream error_message;

        error_message << filename;

        if (message.size() > 0){
            error_message << ": " << message;
        }

        return error_message.str().c_str();
    }

};