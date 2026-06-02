class Planner:

    SEPARATORS = [
        " and ",
        " then ",
        ","
    ]

    @classmethod
    def split_command(cls, text):

        commands = [text]

        for sep in cls.SEPARATORS:

            new_commands = []

            for cmd in commands:
                new_commands.extend(cmd.split(sep))

            commands = new_commands

        return [c.strip() for c in commands if c.strip()]