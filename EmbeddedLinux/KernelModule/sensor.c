#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>

#include <linux/kobject.h>
#include <linux/sysfs.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/string.h>
#include <linux/random.h>

static struct kobject *ksensor;
static unsigned int status;

static ssize_t status_show(struct kobject *o, struct kobj_attribute *a, char *b)
{
    printk(KERN_INFO "Module-Sensor sensor_show\n");
    get_random_bytes(&status, sizeof(status));
    return sprintf(b, "%u\n", status % 1000);
}

static ssize_t status_store(struct kobject *o, struct kobj_attribute *a, char *b, size_t c)
{
    printk(KERN_INFO "Module-Sensor sensor_store\n");
    return c;
}

static struct kobj_attribute sensor_attr = __ATTR(
    status, 
    0660, 
    status_show, 
    status_store
);

static int __init sensor_init(void)
{
    int error;
    printk(KERN_INFO "Module-Sensor Hello!\n");

    ksensor = kobject_create_and_add("sensor", kernel_kobj);
    if (!ksensor) {
        printk(KERN_ERR "Module-Sensor failed to create sensor\n");
        return -ENOMEM;
    }

    error = sysfs_create_file(ksensor, &sensor_attr.attr);
    if (error) {
        printk(KERN_ERR "Module-Sensor failed to create sensor/status\n");
        return error;
    }

    return 0;
}

static void __exit sensor_exit(void)
{
    printk(KERN_INFO "Module-Sensor Bye!\n");
    kobject_put(ksensor);
}

MODULE_LICENSE("GPL");
MODULE_AUTHOR("ikcaro");
MODULE_DESCRIPTION("My Sensor Linux Kernel Module");

module_init(sensor_init);
module_exit(sensor_exit);
