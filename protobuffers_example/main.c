/**
 * To compile example.proto run in project folder:
 * protoc --nanopb_out ./ radiomodem.proto
 */

#include <stdbool.h>
#include <stdint.h>

#include "example.pb.h"

#define MAX_NUMBERS 32

uint8_t buffer[128];
size_t total_bytes_encoded = 0;

typedef struct {
  int32_t numbers[MAX_NUMBERS];
  int32_t numbers_count;
} IntList;

// add a number to the int list
void IntList_add_number(IntList *list, int32_t number) {
  if (list->numbers_count < MAX_NUMBERS) {
    list->numbers[list->numbers_count] = number;
    list->numbers_count++;
  }
}

// Encoding callback must iterate through the list, and write the protobuf tag
// and the value for each item in the list
bool SimpleMessage_encode_numbers(pb_ostream_t *ostream,
                                  const pb_field_t *field, void *const *arg) {
  IntList *source = (IntList *)(*arg);

  // encode all numbers
  for (int i = 0; i < source->numbers_count; i++) {
    if (!pb_encode_tag_for_field(ostream, field)) {
      const char *error = PB_GET_ERROR(ostream);
      printf("SimpleMessage_encode_numbers error: %s", error);
      return false;
    }

    if (!pb_encode_svarint(ostream, source->numbers[i])) {
      const char *error = PB_GET_ERROR(ostream);
      printf("SimpleMessage_encode_numbers error: %s", error);
      return false;
    }
  }

  return true;
}

// Decoding callback is called once for each item, and "appends" to the list
bool SimpleMessage_decode_single_number(pb_istream_t *istream,
                                        const pb_field_t *field, void **arg) {
  IntList *dest = (IntList *)(*arg);

  // decode single number
  int64_t number;
  if (!pb_decode_svarint(istream, &number)) {
    const char *error = PB_GET_ERROR(istream);
    printf("SimpleMessage_decode_single_number error: %s", error);
    return false;
  }

  // add to destination list
  IntList_add_number(dest, (int32_t)number);
  return true;
}

int main(void) {
  // encoding
  {
    // prepare the actual "variable" array
    IntList actualData = {0};
    IntList_add_number(&actualData, 123);
    IntList_add_number(&actualData, 456);
    IntList_add_number(&actualData, 789);

    // prepare the nanopb ENCODING callback
    SimpleMessage msg = SimpleMessage_init_zero;
    msg.number.arg = &actualData;
    msg.number.funcs.encode = SimpleMessage_encode_numbers;

    // call nanopb
    pb_ostream_t ostream = pb_ostream_from_buffer(buffer, sizeof(buffer));
    if (!pb_encode(&ostream, SimpleMessage_fields, &msg)) {
      const char *error = PB_GET_ERROR(&ostream);
      printf("pb_encode error: %s", error);
      return;
    }

    total_bytes_encoded = ostream.bytes_written;
    printf("Encoded size: %d", total_bytes_encoded);
  }

  // decoding
  {
    // empty array for decoding
    IntList decodedData = {0};

    // prepare the nanopb DECODING callback
    SimpleMessage msg = SimpleMessage_init_zero;
    msg.number.arg = &decodedData;
    msg.number.funcs.decode = SimpleMessage_decode_single_number;

    // call nanopb
    pb_istream_t istream = pb_istream_from_buffer(buffer, total_bytes_encoded);
    if (!pb_decode(&istream, SimpleMessage_fields, &msg)) {
      const char *error = PB_GET_ERROR(&istream);
      printf("pb_decode error: %s", error);
      return;
    }

    printf("Bytes decoded: %d", total_bytes_encoded - istream.bytes_left);
  }
}