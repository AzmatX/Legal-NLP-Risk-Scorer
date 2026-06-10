class ContractValidator:

    MIN_TEXT_LENGTH = 20

    def validate(self, file_name: str, text: str) -> bool:

        if not file_name:
            raise ValueError("File name is required")

        if not text:
            raise ValueError("Contract text is empty")

        if len(text.strip()) < self.MIN_TEXT_LENGTH:
            raise ValueError(
                f"Contract text must contain at least {self.MIN_TEXT_LENGTH} characters"
            )

        return True